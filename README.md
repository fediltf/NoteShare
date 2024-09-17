![Chat sys1](https://github.com/user-attachments/assets/7e4f9b8b-94ee-4645-a3f1-d7e0a621c7aa)# NoteShare
NoteShare is an AI-driven platform designed for Tunisian university students to share, access, and collaborate on academic documents. The platform features advanced functionalities such as document recommendation, a messaging system, duplication tests, and an efficient search engine to enhance the educational experience.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Contact](#contact)


## Features
- **Document Sharing:** Easily upload and share academic materials with other students.
- **Duplication Test:** Ensure uploaded materials are original and reliable through advanced duplication testing.
- **Document Recommendation:** AI-powered recommendations to suggest relevant study materials based on user behavior and preferences.
- **Chat System:** Real-time messaging system allowing students to communicate and collaborate directly.
- **Advanced Search:** Search documents efficiently using a robust full-text search mechanism.
- **User Profile Management:** Manage user accounts with secure authentication.

## Technologies Used
- **Frontend:** HTML, CSS, JavaScript, BootStrap
- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **AI & ML:** Python libraries for OCR, NLP, and recommendation algorithms
- **WebSockets:** Enabled real-time communication through Django Channels
- **Other Tools:** Django REST Framework, Postgres Full-Text Search, Redis for message handling

## Screenshots
Here are some screenshots showcasing the NoteShare app:

- **Landing Page**
![Landing page](https://github.com/user-attachments/assets/6fc5192a-29f8-497c-bcb7-fd03a17c2b22)

- **Login & Sign Up**
![Login](https://github.com/user-attachments/assets/04b6f060-1453-47c7-bccf-80f3d588f730)
![signup](https://github.com/user-attachments/assets/9e073757-624d-4822-a64a-97f8aa99bebd)
- **Student Dasahboard**
![Student Dashboard](https://github.com/user-attachments/assets/c63b23e0-c4fb-4561-91f7-cc120649a07e)

- **Document Search by Keywords**
![search](https://github.com/user-attachments/assets/1c988dc8-075f-4274-8fd4-1ffa1ee6dd44)


- **Wallet System**
![wallet sys](https://github.com/user-attachments/assets/3766d301-3f86-4ff8-b2ef-48ab187492c2)

- **Real Time Chat System**
![Chat sys1](https://github.com/user-attachments/assets/0f92d431-739e-48b3-b58b-a42ab87f4c05)
![Chat sys2](https://github.com/user-attachments/assets/d1c4b3ee-a9fb-45de-98dd-90f434da27c8)


## Getting Started

To get a local copy of the project up and running, follow these simple steps:

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Django
- PostgreSQL
- Redis (for real-time messaging with Django Channels)
- Virtual Environment

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fediltf/PFE_NoteShare.git
   cd noteshare
2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
4. **Set up PostgreSQL:**
   - Create a PostgreSQL database and user.
   - Update the DATABASES setting in settings.py with your database details.
5. **Run migrations:**
   ```bash
   python manage.py migrate
6. **Start Redis: Make sure Redis is running on your system.**
   ```bash
   redis-server

7. **Run the development server:**
    ```bash
    python manage.py runserver
8. **Access the application:** Open your web browser and go to http://127.0.0.1:8000.


## Contact
If you have any questions, feel free to contact me at 
[![Outlook](https://img.shields.io/badge/-outlook?style=social&logo=minutemailer&logoColor=blue&label=mohamedfedi.letaief%40eniso.u-sousse.tn&color=grey)](mailto:mohamedfedi.letaief@eniso.u-sousse.tn)
