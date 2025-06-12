# IPv6 Updater Client

This project is a flexible client for updating dynamic DNS (DynDNS) services with your current IPv4 and/or IPv6 addresses. It is designed to run as a Docker container or as a standalone Python script, and supports multiple jobs and updaters, making it suitable for home servers, VPS, or any Linux system with a dynamic IP.

## Features
- **Multiple parser support:**   
Can use different parsers, such as parsing the output from the `ip` command.  
You can easily add your own parser to support other sources or formats.
- **DynDNS update:** Supports updating DynDNS providers (e.g., Strato) with your current IPs.
- **Configurable:** Supports multiple jobs and updaters via a YAML config file.
- **Docker-ready:** Easily deployable as a Docker container.
- **Extensible:** Add your own updaters or parsers as needed.

## Usage

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/ipv6_updater.git
cd ipv6_updater
```

### 2. Configure

Copy `config_blank.yaml` to `config.yaml` and edit it to match your network interface and DynDNS provider credentials:

```sh
cp config_blank.yaml config.yaml
```

Edit `config.yaml`:

```yaml
jobs:
  - name: example_job
    parser:
      type: IPCommandParser
      scope: global
      command_timeout: 5
      interface: eth0            # Replace with your network interface
      fetch_ipv6: true
      fetch_ipv4: false
      ipv6_index: 0              # Use 0 for the first IPv6 address, or adjust as needed
    updaters:
      - type: StratoUpdater      # Or your own updater
        username: "your_username"
        password: "your_password"
        domain: "your.domain.com"
```

**Config parameters:**
- `type`: The parser or updater class to use (e.g., `IPCommandParser`, `StratoUpdater`).
- `scope`: Address scope to filter (usually `global`).
- `command_timeout`: Timeout for the IP detection command.
- `interface`: Network interface to monitor (e.g., `eth0`, `eno1`).
- `fetch_ipv6` / `fetch_ipv4`: Enable or disable fetching of IPv6/IPv4 addresses.
- `ipv6_index` / `ipv4_index`: Which address to use (0 for first, or omit for all).
- Updater-specific parameters (e.g., `username`, `password`, `domain`).


### 3. Run Updater
You can run it either directly on the host or by running a docker container.


#### 3.1. Directly on Host
You can also run the client directly with Python:

```sh
python main.py
```

Or as a daemon:

```sh
python main.py --daemon
```

#### 3.2. Container

Build the Docker image:

```sh
docker build -t ipv6-dyndns .
```

**Recommended:** Use the host network and required capabilities for full interface access:

```sh
docker run -d \
    --name ipv6-dyndns \
    --network host \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    --restart unless-stopped \
    -v $(pwd)/config.yaml:/app/config.yaml:ro \
    ipv6-dyndns
```

You can also run it as a one-shot command (not as a daemon):

```sh
docker run --rm --network host --cap-add=NET_ADMIN --cap-add=NET_RAW -v $(pwd)/config.yaml:/app/config.yaml:ro ipv6-dyndns
```



## Requirements

- Linux host (for `ip` command)
- Python 3.12 (handled by Docker)
- Docker (for containerized usage)

## Extending

You can add your own updaters in the `updaters/` folder or parsers in the `parsers/` folder. Just follow the structure of the existing classes.

## License

MIT License

## Contributing

Contributions are welcome! If you have a use case for a different DynDNS provider or a unique way to parse IP addresses, please consider contributing your own **updater** or **parser**.

- Add your custom updater to the `updaters/` folder.
- Add your custom parser to the `parsers/` folder.
- Follow the structure of the existing classes for easy integration.
- Feel free to open a pull request with your changes and improvements.

Your contributions help make this project more useful for everyone!

---

**This client is not affiliated with any DynDNS provider. Use at your own risk.**