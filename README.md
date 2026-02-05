
### Mero-Lagani

mero-lagani is an automated market monitoring system that helps users stay updated with company listings and market activities without manual effort. It is built to make financial data easier to access by automatically collecting and organizing information that would normally require repeated manual checks.

At the heart of the system is an automation engine that uses Selenium to navigate websites and collect important market data. This process runs automatically in the background, so users always get up-to-date information without needing to visit multiple platforms themselves. The system is designed to handle modern, dynamic websites reliably.

To keep the system fast and efficient, mero-lagani uses Redis to store the latest collected data. This allows the application to quickly serve information without running the automation process every time. A scheduled refresh updates the data daily, ensuring it stays current while keeping system resources under control.

mero-lagani is built with scalability and reliability in mind. Long-running data collection tasks are handled separately using a task queue, which keeps the main application responsive. The modular design makes it easy to extend the system and integrate it into larger financial platforms in the future.