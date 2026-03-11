from dataclasses import dataclass, asdict
from typing import Dict, Any
import json

@dataclass
class User:
    """User model for welcome messages"""
    user_id: str
    name: str
    email: str
    mobile: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert user to JSON string"""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        return User(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            mobile=data['mobile']
        )


@dataclass
class WelcomeMessage:
    """Welcome message model"""
    message_type: str
    user: User
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_type': self.message_type,
            'user': self.user.to_dict(),
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WelcomeMessage':
        """Create message from dictionary"""
        return WelcomeMessage(
            message_type=data['message_type'],
            user=User.from_dict(data['user']),
            timestamp=data['timestamp']
        )
