def require(*required_keys):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for key in required_keys:
                if key not in kwargs:
                    raise ValueError(f"Missing required argument: {key}")
            return func(*args, **kwargs)
        return wrapper
    return decorator