# Tech Context

## Technologies Used
- Python 3
- UDP sockets for communication
- Multicast networking for discovery and leader queries
- `click` for server CLI

## Development Setup
- Run server instances with `python server.py <port>`
- Run clients with `python client.py`
- Configure multicast settings in `config.py`

## Technical Constraints
- Uses UDP; message ordering and reliability handled at application level.
- CLI-driven interface (no GUI or web client).
- Relies on multicast group reachability for discovery.

## Dependencies
- `click` (see `requirements.txt`)

## Tooling Patterns
- No build system; direct Python execution.
- Uses local network interfaces for UDP multicast.

## Recent Technical Improvements
- **Error Handling**: Enhanced socket error handling and timeout management
- **Logging**: Improved log formatting with color coding for better readability
- **Network Stability**: Fixed multicast socket binding issues on macOS with SO_REUSEPORT
- **Data Integrity**: Fixed set/list conversion issues in state replication
- **Performance**: Optimized FO multicast retransmission frequency to reduce log spam

## Code Quality Enhancements
- Added comprehensive error checking for all message types
- Improved validation of client authentication tokens
- Enhanced leader election robustness with retry mechanisms
- Added proper cleanup and shutdown handling