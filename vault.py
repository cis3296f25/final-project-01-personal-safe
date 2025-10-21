from typing import Dict, List, Tuple
import storage


class Vault:
    def __init__(self) -> None:
        self._data: Dict[str, str] = storage.load_vault()

    def add(self, site: str, pwd: str) -> None:
        if not site or not pwd:
            return
        self._data[site] = pwd
        storage.save_vault(self._data)

    def items(self) -> List[Tuple[str, str]]:
        return list(self._data.items())

    def is_empty(self) -> bool:
        return not self._data
    
    def get_sites(self) -> List[str]:
        #Return list of site names
        return list(self._data.keys())
    
    def delete(self, site: str) -> bool:
        #Delete entry by site name
        #true if deleted, false if not found
        if site in self._data:
            del self._data[site]
            storage.save_vault(self._data)
            return True
        return False