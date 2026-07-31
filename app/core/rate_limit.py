from slowapi import Limiter
from slowapi.util import get_remote_address

# kullanıcının IP adresini baz alarak bir sınırlayıcı oluşturur
# Böylece her bir IP adresi kendi kotasını kullanacak
limiter = Limiter(key_func=get_remote_address)