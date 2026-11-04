"""Storage tests need the provider fixtures. Other tests do not."""

pytest_plugins = "test.storage.fixtures"
