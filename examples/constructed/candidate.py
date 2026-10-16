"""In-memory identity routing exercise: never makes network requests."""
class IdentityRoute:
    def choose(self, primary_healthy, standby_healthy, standby_verified):
        if primary_healthy:
            return 'primary'
        if standby_healthy and standby_verified:
            return 'standby'
        raise RuntimeError('identity unavailable: fail closed')
