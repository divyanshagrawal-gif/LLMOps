import hashlib
import json
import redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

class CacheService:
    def _key(self, prompt, model, temperature):
        raw = f"{prompt}:{model}:{temperature}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt, model, temperature):
        key = self._key(prompt, model, temperature)
        value = redis_client.get(key)
        return json.loads(value) if value else None

    def set(self, prompt, model, temperature, response, ttl=3600):
        key = self._key(prompt, model, temperature)
        redis_client.setex(key, ttl, json.dumps(response))
