"""Models for backend internal use"""

from dataclasses import dataclass

@dataclass
class Message:
    title: str
    to_email: str
    subject: str
    content: str

    def __repr__(self) -> str:
        return f"{self.title}\n{"="*20}\nTo: {self.to_email}\nSubject: {self.subject}\n{"-"*20}\n{self.content}"