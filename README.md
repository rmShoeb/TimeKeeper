# TimeKeeper

**TimeKeeper** is a full-stack automated asset tracking system designed to manage warranties, licenses, and subscriptions. It features a modern **Angular 18** frontend (built with Signals and Zoneless change detection) and a robust **FastAPI** backend with background job scheduling.

## Key Features

###  Functionality

* **Automated Reminders:** Background scheduler (APScheduler) runs daily jobs to check for expiring items.  
* **Secure Authentication:** Passwordless Email-OTP login flow with JWT session management.  
* **Smart Validation:** Three-layer date validation preventing past dates (HTML5 \+ Blur \+ Submit).  
* **Multi-Tenancy:** Complete data isolation per user.

### Technical Highlights (Frontend)

* **Zoneless Architecture:** Zone.js removed for a \~50KB bundle size reduction and better performance.  
* **Signal-Based State:** Extensive use of `signal()`, `computed()`, and `model()` for fine-grained reactivity.  
* **Modern Control Flow:** Uses the new `@if`, `@for` syntax throughout.  
* **Smart/Presentational Pattern:** Clean separation between Logic Containers (Dashboard) and UI Components (Tables/Modals).

### Technical Highlights (Backend)

* **Async Architecture:** Fully async Python endpoints using FastAPI.  
* **Smart Scheduler:** Database-backed job tracking that automatically runs missed jobs upon server restart.  
* **Security First:** SQL Injection protection (ORM), XSS sanitization, and cryptographic OTP generation.

## Tech Stack

| Domain | Technology |
| :---- | :---- |
| **Frontend** | Angular 18+, Bootstrap 5, Flatpickr |
| **Backend** | Python 3.10+, FastAPI, SQLModel (SQLAlchemy), Pydantic |
| **Database** | SQLite / PostgreSQL |
| **Scheduling** | APScheduler (AsyncIO) |

## Installation & Running

Follow these steps mentioed [here](./build/README.md) to set up the project locally.

**Access the App**

* **Frontend:** http://localhost:4200  
* **API Docs:** http://localhost:8000/docs

## Architecture Overview

The project follows a clean, modular architecture:

```
├── backend/
│   ├── app/
│   │   ├── routers/       # API Endpoints
│   │   ├── crud/          # Database Queries
│   │   ├── models.py      # SQLModel Definitions
│   │   ├── scheduler.py   # Background Jobs
│   │   └── main.py        # Entry Point
│  
├── frontend/
│   ├── src/app/
│   │   ├── components/    # Standalone Components
│   │   │   ├── dashboard/ # Smart Container
│   │   │   └── ...        # Presentational Components
│   │   ├── services/      # API Communication
│   │   └── guards/        # Route Protection
```

## License

This project is open source and available under the MIT License.