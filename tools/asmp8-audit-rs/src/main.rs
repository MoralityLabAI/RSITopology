use std::env;
use std::process::ExitCode;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, mpsc};
use std::thread;
use std::time::Instant;

const OUTCOMES: usize = 64;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Family {
    Diffuse,
    Heteroskedastic,
    RareTail,
}

impl Family {
    fn parse(value: &str) -> Result<Self, String> {
        match value {
            "diffuse_low_error" => Ok(Self::Diffuse),
            "heteroskedastic_proxy_coupled" => Ok(Self::Heteroskedastic),
            "rare_top_tail" => Ok(Self::RareTail),
            _ => Err(format!("unsupported error family: {value}")),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Diffuse => "diffuse_low_error",
            Self::Heteroskedastic => "heteroskedastic_proxy_coupled",
            Self::RareTail => "rare_top_tail",
        }
    }

    fn population(self) -> [f64; OUTCOMES] {
        let mut values = [0.0; OUTCOMES];
        for (index, value) in values.iter_mut().enumerate() {
            *value = match self {
                Self::Diffuse => ((index % 5) as f64 - 2.0) * 0.025,
                Self::Heteroskedastic => {
                    let rank = index as f64 / (OUTCOMES - 1) as f64;
                    -0.30 * rank * rank + if index % 2 == 0 { 0.025 } else { -0.025 }
                }
                Self::RareTail => {
                    if index >= OUTCOMES - 2 {
                        -1.0
                    } else {
                        0.0
                    }
                }
            };
        }
        values
    }
}

#[derive(Clone, Debug)]
struct Config {
    audits_per_stream: u64,
    streams: usize,
    workers: usize,
    seed: u64,
    family: Family,
    familywise_alpha: f64,
    checkpoint_count: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            audits_per_stream: 8192,
            streams: 1024,
            workers: thread::available_parallelism().map_or(1, usize::from),
            seed: 80_520_260_723,
            family: Family::Diffuse,
            familywise_alpha: 0.05,
            checkpoint_count: 16,
        }
    }
}

#[derive(Clone, Copy, Debug)]
struct StreamResult {
    stream: usize,
    u1: f64,
    u2: f64,
}

#[derive(Clone, Debug)]
struct Summary {
    family: Family,
    audits_per_stream: u64,
    streams: usize,
    workers: usize,
    total_audits: u128,
    elapsed_seconds: f64,
    audits_per_second: f64,
    mean_u1: f64,
    mean_u2: f64,
    checksum: u64,
    peak_working_set_bytes: u64,
}

#[cfg(windows)]
fn peak_working_set_bytes() -> u64 {
    use std::ffi::c_void;
    use std::mem::size_of;

    #[repr(C)]
    struct ProcessMemoryCounters {
        cb: u32,
        page_fault_count: u32,
        peak_working_set_size: usize,
        working_set_size: usize,
        quota_peak_paged_pool_usage: usize,
        quota_paged_pool_usage: usize,
        quota_peak_non_paged_pool_usage: usize,
        quota_non_paged_pool_usage: usize,
        pagefile_usage: usize,
        peak_pagefile_usage: usize,
    }

    #[link(name = "kernel32")]
    unsafe extern "system" {
        fn GetCurrentProcess() -> *mut c_void;
    }
    #[link(name = "psapi")]
    unsafe extern "system" {
        fn GetProcessMemoryInfo(
            process: *mut c_void,
            counters: *mut ProcessMemoryCounters,
            size: u32,
        ) -> i32;
    }

    let mut counters = ProcessMemoryCounters {
        cb: size_of::<ProcessMemoryCounters>() as u32,
        page_fault_count: 0,
        peak_working_set_size: 0,
        working_set_size: 0,
        quota_peak_paged_pool_usage: 0,
        quota_paged_pool_usage: 0,
        quota_peak_non_paged_pool_usage: 0,
        quota_non_paged_pool_usage: 0,
        pagefile_usage: 0,
        peak_pagefile_usage: 0,
    };
    // SAFETY: both APIs are read-only process queries; the structure size and
    // writable pointer are supplied exactly as required by PSAPI.
    let succeeded = unsafe {
        GetProcessMemoryInfo(
            GetCurrentProcess(),
            &mut counters,
            size_of::<ProcessMemoryCounters>() as u32,
        )
    };
    if succeeded == 0 {
        0
    } else {
        counters.peak_working_set_size as u64
    }
}

#[cfg(not(windows))]
fn peak_working_set_bytes() -> u64 {
    0
}

fn splitmix64(mut value: u64) -> u64 {
    value = value.wrapping_add(0x9e37_79b9_7f4a_7c15);
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^ (value >> 31)
}

fn sampled_index(seed: u64, stream: usize, audit: u64) -> usize {
    let counter = seed
        ^ (stream as u64).wrapping_mul(0xd2b7_4407_b1ce_6e93)
        ^ audit.wrapping_mul(0xca5a_8263_9512_1157);
    (splitmix64(counter) & (OUTCOMES as u64 - 1)) as usize
}

fn empirical_upper(mean: f64, variance: f64, n: u64, log_term: f64) -> f64 {
    if n <= 1 {
        return 1.0;
    }
    (mean + (2.0 * variance * log_term / n as f64).sqrt() + 7.0 * log_term / (3.0 * (n - 1) as f64))
        .min(1.0)
}

fn run_stream(
    stream: usize,
    config: &Config,
    errors: &[f64; OUTCOMES],
    log_term: f64,
) -> StreamResult {
    let mut sum_z1 = 0.0;
    let mut sum_z1_squared = 0.0;
    let mut sum_z2 = 0.0;
    let mut sum_z2_squared = 0.0;
    for audit in 0..config.audits_per_stream {
        let error = errors[sampled_index(config.seed, stream, audit)];
        let z1 = error.abs();
        let z2 = error * error;
        sum_z1 += z1;
        sum_z1_squared += z1 * z1;
        sum_z2 += z2;
        sum_z2_squared += z2 * z2;
    }
    let n = config.audits_per_stream;
    let n_float = n as f64;
    let mean_z1 = sum_z1 / n_float;
    let mean_z2 = sum_z2 / n_float;
    let variance_z1 =
        (n_float * (sum_z1_squared / n_float - mean_z1 * mean_z1) / (n_float - 1.0)).max(0.0);
    let variance_z2 =
        (n_float * (sum_z2_squared / n_float - mean_z2 * mean_z2) / (n_float - 1.0)).max(0.0);
    StreamResult {
        stream,
        u1: empirical_upper(mean_z1, variance_z1, n, log_term),
        u2: empirical_upper(mean_z2, variance_z2, n, log_term).sqrt(),
    }
}

fn run(config: &Config) -> Result<Summary, String> {
    if config.audits_per_stream <= 1 {
        return Err("audits-per-stream must exceed one".to_owned());
    }
    if config.streams == 0 || config.workers == 0 {
        return Err("streams and workers must be positive".to_owned());
    }
    if !(0.0..1.0).contains(&config.familywise_alpha) || config.checkpoint_count == 0 {
        return Err("familywise-alpha and checkpoint-count are invalid".to_owned());
    }
    let errors = Arc::new(config.family.population());
    let config = Arc::new(config.clone());
    let delta = config.familywise_alpha / (2.0 * config.checkpoint_count as f64);
    let log_term = (2.0 / delta).ln();
    let next = Arc::new(AtomicUsize::new(0));
    let workers = config.workers.min(config.streams);
    let (sender, receiver) = mpsc::channel::<StreamResult>();
    let started = Instant::now();

    thread::scope(|scope| {
        for _ in 0..workers {
            let sender = sender.clone();
            let next = Arc::clone(&next);
            let config = Arc::clone(&config);
            let errors = Arc::clone(&errors);
            scope.spawn(move || {
                loop {
                    let stream = next.fetch_add(1, Ordering::Relaxed);
                    if stream >= config.streams {
                        break;
                    }
                    let result = run_stream(stream, &config, &errors, log_term);
                    if sender.send(result).is_err() {
                        break;
                    }
                }
            });
        }
        drop(sender);
    });

    let mut results: Vec<StreamResult> = receiver.into_iter().collect();
    if results.len() != config.streams {
        return Err(format!(
            "worker pool returned {} of {} streams",
            results.len(),
            config.streams
        ));
    }
    results.sort_unstable_by_key(|result| result.stream);
    let elapsed_seconds = started.elapsed().as_secs_f64();
    let total_audits = config.audits_per_stream as u128 * config.streams as u128;
    let mean_u1 = results.iter().map(|result| result.u1).sum::<f64>() / config.streams as f64;
    let mean_u2 = results.iter().map(|result| result.u2).sum::<f64>() / config.streams as f64;
    let checksum = results.iter().fold(0_u64, |accumulator, result| {
        accumulator
            ^ result.u1.to_bits().rotate_left((result.stream % 64) as u32)
            ^ result
                .u2
                .to_bits()
                .rotate_right((result.stream % 64) as u32)
    });
    Ok(Summary {
        family: config.family,
        audits_per_stream: config.audits_per_stream,
        streams: config.streams,
        workers,
        total_audits,
        elapsed_seconds,
        audits_per_second: total_audits as f64 / elapsed_seconds,
        mean_u1,
        mean_u2,
        checksum,
        peak_working_set_bytes: peak_working_set_bytes(),
    })
}

fn parse_u64(value: Option<String>, name: &str) -> Result<u64, String> {
    value
        .ok_or_else(|| format!("{name} requires a value"))?
        .parse()
        .map_err(|_| format!("invalid {name}"))
}

fn parse_usize(value: Option<String>, name: &str) -> Result<usize, String> {
    let parsed = parse_u64(value, name)?;
    usize::try_from(parsed).map_err(|_| format!("{name} is too large"))
}

fn parse_f64(value: Option<String>, name: &str) -> Result<f64, String> {
    value
        .ok_or_else(|| format!("{name} requires a value"))?
        .parse()
        .map_err(|_| format!("invalid {name}"))
}

fn parse_args() -> Result<Config, String> {
    let mut config = Config::default();
    let mut arguments = env::args().skip(1);
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--audits-per-stream" => {
                config.audits_per_stream = parse_u64(arguments.next(), &argument)?;
            }
            "--streams" => config.streams = parse_usize(arguments.next(), &argument)?,
            "--workers" => config.workers = parse_usize(arguments.next(), &argument)?,
            "--seed" => config.seed = parse_u64(arguments.next(), &argument)?,
            "--family" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| "--family requires a value".to_owned())?;
                config.family = Family::parse(&value)?;
            }
            "--familywise-alpha" => {
                config.familywise_alpha = parse_f64(arguments.next(), &argument)?;
            }
            "--checkpoint-count" => {
                config.checkpoint_count = parse_usize(arguments.next(), &argument)?;
            }
            "--help" | "-h" => {
                println!(
                    "asmp8-audit [--audits-per-stream N] [--streams N] [--workers N] \
                     [--seed N] [--family NAME] [--familywise-alpha X] \
                     [--checkpoint-count N]"
                );
                std::process::exit(0);
            }
            _ => return Err(format!("unknown argument: {argument}")),
        }
    }
    Ok(config)
}

fn json(summary: &Summary) -> String {
    format!(
        concat!(
            "{{\n",
            "  \"schema_version\": \"asmp8_parallel_audit_benchmark_v0_1\",\n",
            "  \"family\": \"{}\",\n",
            "  \"audits_per_stream\": {},\n",
            "  \"streams\": {},\n",
            "  \"workers\": {},\n",
            "  \"total_audits\": {},\n",
            "  \"elapsed_seconds\": {:.9},\n",
            "  \"audits_per_second\": {:.6},\n",
            "  \"mean_empirical_bernstein_u1\": {:.17},\n",
            "  \"mean_empirical_bernstein_u2\": {:.17},\n",
            "  \"deterministic_checksum\": \"{:016x}\",\n",
            "  \"peak_working_set_bytes\": {},\n",
            "  \"model_forward_included\": false,\n",
            "  \"claim_boundary\": \"Counter-based synthetic sampling and moment reduction only; no model inference and no replacement of sealed v0.5 artifacts.\"\n",
            "}}\n"
        ),
        summary.family.name(),
        summary.audits_per_stream,
        summary.streams,
        summary.workers,
        summary.total_audits,
        summary.elapsed_seconds,
        summary.audits_per_second,
        summary.mean_u1,
        summary.mean_u2,
        summary.checksum,
        summary.peak_working_set_bytes,
    )
}

fn main() -> ExitCode {
    match parse_args().and_then(|config| run(&config)) {
        Ok(summary) => {
            print!("{}", json(&summary));
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("{message}");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn populations_match_registered_formulas() {
        let diffuse = Family::Diffuse.population();
        assert_eq!(diffuse[0], -0.05);
        assert_eq!(diffuse[2], 0.0);
        assert_eq!(diffuse[4], 0.05);
        let rare = Family::RareTail.population();
        assert!(rare[..62].iter().all(|value| *value == 0.0));
        assert_eq!(rare[62], -1.0);
        assert_eq!(rare[63], -1.0);
    }

    #[test]
    fn worker_count_does_not_change_result() {
        let base = Config {
            audits_per_stream: 2048,
            streams: 32,
            workers: 1,
            ..Config::default()
        };
        let serial = run(&base).unwrap();
        let parallel = run(&Config { workers: 4, ..base }).unwrap();
        assert_eq!(serial.checksum, parallel.checksum);
        assert_eq!(serial.mean_u1.to_bits(), parallel.mean_u1.to_bits());
        assert_eq!(serial.mean_u2.to_bits(), parallel.mean_u2.to_bits());
    }

    #[test]
    fn bounds_are_finite_and_in_range() {
        for family in [Family::Diffuse, Family::Heteroskedastic, Family::RareTail] {
            let result = run(&Config {
                audits_per_stream: 128,
                streams: 8,
                workers: 2,
                family,
                ..Config::default()
            })
            .unwrap();
            assert!(result.mean_u1.is_finite() && (0.0..=1.0).contains(&result.mean_u1));
            assert!(result.mean_u2.is_finite() && (0.0..=1.0).contains(&result.mean_u2));
        }
    }
}
