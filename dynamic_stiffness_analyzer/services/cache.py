from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from typing import Any, Dict, Optional


@dataclass
class CacheComputacional:
    """
    Sistema de caché LRU sencillo para resultados de cálculos costosos.
    """

    max_cache_size: int = 50
    cache: Dict[str, Any] = field(default_factory=dict)
    cache_access_times: Dict[str, datetime] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    def generar_hash_parametros(self, *args: Any, **kwargs: Any) -> Optional[str]:
        try:
            parametros_str = f"{args}_{sorted(kwargs.items())}"
            return hashlib.md5(parametros_str.encode()).hexdigest()
        except Exception:
            return None

    def obtener_de_cache(self, cache_key: Optional[str]) -> Optional[Any]:
        if cache_key and cache_key in self.cache:
            self.cache_access_times[cache_key] = datetime.now()
            self.hits += 1
            return self.cache[cache_key]
        self.misses += 1
        return None

    def guardar_en_cache(self, cache_key: Optional[str], resultado: Any) -> None:
        if not cache_key:
            return
        if len(self.cache) >= self.max_cache_size:
            oldest_key = min(self.cache_access_times.keys(), key=lambda k: self.cache_access_times[k])
            self.cache.pop(oldest_key, None)
            self.cache_access_times.pop(oldest_key, None)
        self.cache[cache_key] = resultado
        self.cache_access_times[cache_key] = datetime.now()

    def limpiar_cache(self) -> None:
        self.cache.clear()
        self.cache_access_times.clear()
        self.hits = 0
        self.misses = 0

    def estadisticas_cache(self) -> Dict[str, Any]:
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
        }


# Instancia global reutilizable (inyectable si se desea)
CACHE = CacheComputacional()


