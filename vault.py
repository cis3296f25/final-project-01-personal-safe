from typing import Dict, List, Tuple
import storage


class Vault:
    def __init__(self, master_password: str) -> None:
        # load_vault now requires a master password to derive the key
        self._master_password = master_password
        self._data: Dict[str, str] = storage.load_vault(master_password)

    def add(self, site: str, pwd: str) -> None:
        if not site or not pwd:
            return
        self._data[site] = pwd
        storage.save_vault(self._data, self._master_password)

    def items(self) -> List[Tuple[str, str]]:
        return list(self._data.items())

    def is_empty(self) -> bool:
        return not self._data

    def get_sites(self) -> List[str]:
        # Return list of site names
        return list(self._data.keys())

    def delete(self, site: str) -> bool:
        # Delete entry by site name
        # true if deleted, false if not found
        if site in self._data:
            del self._data[site]
            storage.save_vault(self._data, self._master_password)
            return True
        return False
