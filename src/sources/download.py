"""
Purpose of this code is to act as a script that can be ran to download videos 
depending on the websource extracted

"""
import argparse
import sys

from youtube import YouTubeFetcher


FETCHERS = {
    "youtube": YouTubeFetcher,
    # Can add other sources if needed later on 
}

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download video from multiple sources"
    )
    parser.add_argument(
        "-s", "--source",
        choices=FETCHERS.keys(),
        help="Media source (auto-detected if omitted)",
    )
    parser.add_argument("url", help="URL of the video to download")

    return parser.parse_args(argv)


def detect_source(url: str) -> str:
    """Validate if the source being passed is one that we have a fetcher for"""
    for name, fetcher_class in FETCHERS.items():
        if fetcher_class().validate_url(url):
            return name
    return None

def main(argv: list[str] | None = None):
    print(argv)
    args = parse_args(argv)

    #check if the source exits in implemented downloaders
    source = args.source or detect_source(args.url)
    if source is None:
        print(f"Error: Could not detect video source for '{args.url}'.")
        print(f"Specify one explicitly with --source ({', '.join(FETCHERS)})")
        sys.exit(1)

    #get the relevant fetcher
    fetcher = FETCHERS[source]()

    try:
        result = fetcher.download(args.url)
        print(f"\nDone: {result.title}")
        print(f"Saved to: {result.filepath}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()