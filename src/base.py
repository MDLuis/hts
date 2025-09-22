from abc import ABC, abstractmethod

class Source(ABC):
    """
    Abstract base class for tariff data sources.

    - fetch(): retrieve raw data (HTML, API response, file, etc.)
    - parse(): turn raw data into structured Python objects
    - save(): persist structured data (CSV, JSON, DB)
    """

    @abstractmethod
    def fetch(self):
        "Fetch raw data from the source (HTML, API, file, etc.)."
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw_data):
        "Parse raw data into structured Python objects."
        raise NotImplementedError

    @abstractmethod
    def save(self, structured_data, path: str):
        "Save structured data (CSV/JSON/DB) to the given path."
        raise NotImplementedError
