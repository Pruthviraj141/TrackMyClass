"""
Core Application Errors
Standardized Exception mapping ensuring internal logic isn't leaked directly to users.
"""

class TrackMyClassError(Exception):
    """Base application error."""
    pass

class ValidationError(TrackMyClassError):
    """Data validation failure."""
    pass

class AuthenticationError(TrackMyClassError):
    """Identity cannot be verified."""
    pass

class AuthorizationError(TrackMyClassError):
    """Identity verified but lacks permissions."""
    pass

class NotFoundError(TrackMyClassError):
    """Requested resource does not exist."""
    pass

class ConflictError(TrackMyClassError):
    """Resource conflicts with existing state."""
    pass

class RecognitionError(TrackMyClassError):
    """ML Recognition pipeline failure."""
    pass

class SessionError(TrackMyClassError):
    """Attendance session configuration failure."""
    pass

class PersistenceError(TrackMyClassError):
    """Database I/O or connection failure."""
    pass
