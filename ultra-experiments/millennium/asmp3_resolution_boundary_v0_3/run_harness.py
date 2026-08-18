from resolution_harness import build_result, write_result


def main() -> None:
    result = build_result()
    if not result["certified"]:
        raise RuntimeError("ASMP-3 exact harness did not certify")
    write_result(result)
    print("ASMP-3 v0.3 exact resolution-boundary harness certified")


if __name__ == "__main__":
    main()
