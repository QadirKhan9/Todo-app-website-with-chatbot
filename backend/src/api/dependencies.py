from fastapi import Depends
from ..auth import get_current_user


# Re-export commonly used dependencies
CurrentUser = Depends(get_current_user)