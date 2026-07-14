# Spectral-Bundle Discovery Control

## Claim boundary

Synthetic/offline evidence only. A passing result identifies a stable spectral bundle that improves grouped prediction and bounded candidate allocation. It does not establish real-model self-improvement, apply a weight edit, or demonstrate RSI.

This run changes no model weights and performs no reinforcement learning. It tests the mathematical instrument on planted and outcome-null controls.

## Mathematical object

For each frozen Laplacian spectral band, average its prompt-specific projectors implicitly, then retain directions whose projector occupancy is at least 0.75. This is a Grassmannian consensus subspace: a high-dimensional structure stable across contexts, rather than a coordinate tuple at one site.

## Geometry seal

```json
{
  "bands": {
    "high": {
      "basis_sha256": "f82520af46ebf54d2f14d3ad039aecb4bb930596c519022161e4287d6bdaec33",
      "context_ranks": [
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18
      ],
      "occupancies": [
        0.9998542308483368,
        0.9998447052311719,
        0.9998226167548611,
        0.9998180788130131,
        0.9998004425227608,
        0.999787611791831,
        0.9997807898383503,
        0.9997682394912802,
        0.9997613674103568,
        0.9997446126414569,
        0.9997420634592948,
        0.999718145556813,
        0.9997053902394211,
        0.9996930601670564,
        0.9996738415259598,
        0.9996705799686936,
        0.9996654542038491,
        0.9996272578215003
      ],
      "rank": 18
    },
    "low": {
      "basis_sha256": "ec0755aa8ac5dd3ea02886ef9bcf858251e689aa041b3d62adb720a8a0633b03",
      "context_ranks": [
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12
      ],
      "occupancies": [
        0.9997702780535129,
        0.9997547141630758,
        0.9997343544093517,
        0.999726471500771,
        0.9997150667252142,
        0.9996963808343579,
        0.9996809969652901,
        0.9996717751187829,
        0.9996477527466853,
        0.9996425256985555,
        0.9995915808009541,
        0.9995626542542484
      ],
      "rank": 12
    },
    "middle": {
      "basis_sha256": "b0f27e45ca8aedb3aadd2df4fd70a6bd15145bca1c105549d3f5f5c90a05ccc6",
      "context_ranks": [
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18,
        18
      ],
      "occupancies": [
        0.9998449194770646,
        0.9998386775844326,
        0.9998316543136029,
        0.999818174911265,
        0.9997955744484129,
        0.9997917377244878,
        0.999786722158227,
        0.9997619065024489,
        0.9997520824798373,
        0.9997477596302549,
        0.9997394791461088,
        0.9997216359506804,
        0.9997089373105261,
        0.9996895990031915,
        0.9996819500261586,
        0.9996666850167056,
        0.9996590688235171,
        0.9996157597441943
      ],
      "rank": 18
    }
  },
  "baseline_covariate_sha256": "42001eede587f20983bbc061028afd9bba73c0697556e90e6a097fedc4df7be2",
  "candidate_vector_sha256": "bda781b511b524deb92062ae2cdb367184eb8dd28ec266231f2b27d238fd80de",
  "checkpoint_interval": "one_fixture_phase",
  "chunk_strategy": "candidate rows in blocks of 64; mean projector is matrix-free",
  "config_sha256": "e041fd6429c812586ef7000d085583f0454646c3fb4ea4b3c9f1e327ed9c505c",
  "exact_argv": [
    "C:\\Python311\\python.exe",
    "C:\\projects\\RSITopology\\scripts\\run_synthetic_discovery.py",
    "--chunk-rows",
    "64"
  ],
  "laplacian_hashes": {
    "context-00": "ae187314bfbe556322434b28ffb12f75c684a10864cc81fba925a40c701deed7",
    "context-01": "1ea0402eae37f9c60fe00a2c69dca0feabca7eacf573b98d2600836bb75bc050",
    "context-02": "81389bd2812aaa3575f6f342bace32d2a6dce6f475e78f1fa4a00ecbcacc0f2d",
    "context-03": "3c4ff70c35442a33fae75c63520f31425685cea985370b3dd0a50d64dc46c1c9",
    "context-04": "a6111c0d48e89a4f558abf4d3daab387e6437b4aae7edf6141c4255680524bcc",
    "context-05": "f769048850b1d52fe8360336129e9556297988ffbae19cc39f45bf7887d4b8fe",
    "context-06": "40bf55759e14e27776377bad273e502807e372c31045dec20888606720e42ce9",
    "context-07": "29f35657e906d12d37f7e853ee5227a2a474c46df97f54c2b3eaf07c81405bcd",
    "context-08": "ecbd22259c86f14ac8cf885b596c0d62953c5f6f3093f3ead00fcabcd26aeee9",
    "context-09": "6aeeab7b7c9f7e2555d28cebafc31df82e8c86adc9a15de8d54262b73a3be1ca"
  },
  "outcome_hash_present": false,
  "phase": "sealed_geometry_before_outcomes",
  "platform": "Windows-10-10.0.26200-SP0",
  "python": "3.11.4 (tags/v3.11.4:d2340ef, Jun  7 2023, 05:45:37) [MSC v.1934 64 bit (AMD64)]"
}
```

## Planted control

```json
{
  "direct_edit": {
    "haar_advantage": 0.1836794360267507,
    "matched_rank_haar_improvement": 0.12027537289925465,
    "mean_relative_mse_improvement": 0.30395480892600535,
    "passed": true,
    "proposal_direction_sha256": "415ff702a7a3154186d4577fd050c694e07dd2105eea8aca107e85cad7d3c815",
    "status": "proposal_only_not_applied"
  },
  "geometry": {
    "bands": {
      "high": {
        "context_ranks": [
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18
        ],
        "interval": [
          0.65,
          1.000001
        ],
        "minimum_occupancy": 0.9996272578215006,
        "occupancies": [
          0.9998542308483365,
          0.9998447052311713,
          0.9998226167548615,
          0.999818078813013,
          0.9998004425227602,
          0.9997876117918306,
          0.9997807898383498,
          0.9997682394912794,
          0.9997613674103568,
          0.9997446126414562,
          0.9997420634592943,
          0.999718145556812,
          0.9997053902394213,
          0.9996930601670565,
          0.99967384152596,
          0.9996705799686934,
          0.9996654542038484,
          0.9996272578215006
        ],
        "rank": 18
      },
      "low": {
        "context_ranks": [
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12
        ],
        "interval": [
          0.0,
          0.25
        ],
        "minimum_occupancy": 0.9995626542542478,
        "occupancies": [
          0.9997702780535132,
          0.9997547141630757,
          0.9997343544093512,
          0.9997264715007701,
          0.9997150667252139,
          0.9996963808343577,
          0.9996809969652909,
          0.9996717751187827,
          0.9996477527466858,
          0.9996425256985555,
          0.9995915808009544,
          0.9995626542542478
        ],
        "rank": 12
      },
      "middle": {
        "context_ranks": [
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18
        ],
        "interval": [
          0.25,
          0.65
        ],
        "minimum_occupancy": 0.999615759744194,
        "occupancies": [
          0.9998449194770642,
          0.9998386775844323,
          0.9998316543136027,
          0.999818174911265,
          0.9997955744484128,
          0.9997917377244883,
          0.9997867221582274,
          0.9997619065024487,
          0.9997520824798374,
          0.9997477596302548,
          0.9997394791461084,
          0.9997216359506799,
          0.9997089373105256,
          0.9996895990031903,
          0.9996819500261589,
          0.999666685016706,
          0.9996590688235173,
          0.999615759744194
        ],
        "rank": 18
      }
    },
    "minimum_occupancy": 0.9995626542542478,
    "passed": true,
    "selected_band": "low",
    "selected_rank": 12
  },
  "policy": {
    "maximum_kl": 0.05,
    "mean_heldout_return_uplift": 0.03774732580149714,
    "mean_relative_mse_improvement": 0.3933624752538667,
    "passed": true
  }
}
```

## Outcome-null control

```json
{
  "direct_edit": {
    "haar_advantage": -0.002430730778580399,
    "matched_rank_haar_improvement": -0.01094154149034916,
    "mean_relative_mse_improvement": -0.013372272268929558,
    "passed": false,
    "proposal_direction_sha256": "f23bbd55012afd97331dc4bcd761e4dc462a5db18e1b31d8ad7a78a23e0faf06",
    "status": "proposal_only_not_applied"
  },
  "geometry": {
    "bands": {
      "high": {
        "context_ranks": [
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18
        ],
        "interval": [
          0.65,
          1.000001
        ],
        "minimum_occupancy": 0.9996272578215005,
        "occupancies": [
          0.9998542308483365,
          0.9998447052311721,
          0.9998226167548613,
          0.9998180788130132,
          0.99980044252276,
          0.9997876117918311,
          0.9997807898383497,
          0.9997682394912797,
          0.9997613674103566,
          0.9997446126414563,
          0.9997420634592947,
          0.999718145556812,
          0.9997053902394207,
          0.9996930601670567,
          0.9996738415259601,
          0.999670579968693,
          0.9996654542038484,
          0.9996272578215005
        ],
        "rank": 18
      },
      "low": {
        "context_ranks": [
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12,
          12
        ],
        "interval": [
          0.0,
          0.25
        ],
        "minimum_occupancy": 0.9995626542542482,
        "occupancies": [
          0.9997702780535128,
          0.999754714163076,
          0.9997343544093512,
          0.9997264715007708,
          0.9997150667252139,
          0.9996963808343572,
          0.9996809969652909,
          0.9996717751187832,
          0.9996477527466857,
          0.9996425256985555,
          0.9995915808009536,
          0.9995626542542482
        ],
        "rank": 12
      },
      "middle": {
        "context_ranks": [
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18,
          18
        ],
        "interval": [
          0.25,
          0.65
        ],
        "minimum_occupancy": 0.9996157597441944,
        "occupancies": [
          0.9998449194770644,
          0.9998386775844329,
          0.9998316543136027,
          0.999818174911265,
          0.9997955744484127,
          0.9997917377244876,
          0.9997867221582268,
          0.9997619065024491,
          0.999752082479838,
          0.9997477596302551,
          0.9997394791461086,
          0.9997216359506803,
          0.999708937310526,
          0.999689599003191,
          0.999681950026159,
          0.9996666850167055,
          0.9996590688235173,
          0.9996157597441944
        ],
        "rank": 18
      }
    },
    "minimum_occupancy": 0.9995626542542482,
    "passed": true,
    "selected_band": "low",
    "selected_rank": 12
  },
  "policy": {
    "maximum_kl": 0.05,
    "mean_heldout_return_uplift": -0.0034495287442042263,
    "mean_relative_mse_improvement": -0.002145591540000994,
    "passed": false
  }
}
```

The geometry gate is expected to pass in both fixtures because outcomes do not define geometry. The policy and edit gates should pass only when held-out causal utility is planted; otherwise the instrument is leaking or overfitting.
