#!/usr/bin/env python3.5

import json

_SERVER = "134.155.48.8"
_SERVER_PORT = "9202"

data = json.loads(json_string);

print(json.dumps(data, sort_keys=True, indent=4))

class YouTubeMetadataFetcher:
    def __init__(self, server, port):
        self.server = server
        self.port = port


def main():
    print("main")


if __name__ == "__main__":
    main()
