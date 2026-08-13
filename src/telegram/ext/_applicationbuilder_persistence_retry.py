from telegram.ext._application_persistence_retry import Application
from telegram.ext._applicationbuilder import ApplicationBuilder as _ApplicationBuilder


class ApplicationBuilder(_ApplicationBuilder):
    """Application builder using the persistence-safe Application by default."""

    def __init__(self) -> None:
        super().__init__()
        self.application_class(Application)
