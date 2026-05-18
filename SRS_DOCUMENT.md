# School Management System - Software Requirements Specification (SRS)

**Version:** 1.0  
**Project Name:** School Management System  
**Technology Stack:** Django Framework (Python), SQLite Database, HTML/CSS/JavaScript

---

## 1. Introduction

### 1.1 Purpose
This document outlines the complete specifications for a web-based School Management System designed to automate and manage academic processes including admissions, user management, academic records, attendance tracking, and news dissemination.

### 1.2 Target Users
- **Administrators** - Full system access for school management
- **Teachers** - Assignment creation, grade/attendance recording
- **Students** - View assignments, grades, attendance
- **Parents** - Monitor children's academic progress
- **Visitors/Applicants** - Submit online admission applications

---

## 2. System Architecture

### 2.1 Technology Stack
| Component | Technology |
|-----------|------------|
| Backend | Django 4.x |
| Database | SQLite |
| Templates | HTML5 + Django Template Language |
| Styling | CSS (Bootstrap/custom) |
| Authentication | Django built-in auth |

### 2.2 Project Structure
```
school_project/
├── config/          # Django project settings
├── core/            # Public pages (home, about, gallery, contact)
├── accounts/        # User authentication and profiles
├── admissions/      # Online application system
├── academics/       # Academic management
├── news/            # News/announcements management
├── templates/       # HTML templates
├── static/          # CSS, JavaScript, images
└── media/           # User-uploaded files
```

---

## 3. Data Models Specification

### 3.1 Core App Models

#### SchoolInfo
| Field | Type | Description |
|-------|------|-------------|
| name | CharField(200) | School name |
| mission | TextField | Mission statement |
| vision | TextField | Vision statement |
| history | TextField | School history |

#### Staff
| Field | Type | Description |
|-------|------|-------------|
| name | CharField(100) | Staff member name |
| position | CharField(100) | Job title |
| bio | TextField | Biography |
| photo | ImageField | Profile photo |

#### Facility
| Field | Type | Description |
|-------|------|-------------|
| title | CharField(100) | Facility name |
| description | TextField | Facility details |
| image | ImageField | Facility photo |

#### GalleryImage
| Field | Type | Description |
|-------|------|-------------|
| title | CharField(100) | Image title |
| description | TextField | Image description |
| image | ImageField | Gallery image |
| uploaded_at | DateTimeField | Upload timestamp |

---

### 3.2 Accounts App Models

#### StudentProfile
| Field | Type | Description |
|-------|------|-------------|
| user | OneToOneField(User) | Linked user account |
| admission_number | CharField(20) | Unique admission ID |
| grade | CharField(50) | Current grade/class |
| profile_picture | ImageField | Student photo (optional) |

#### TeacherProfile
| Field | Type | Description |
|-------|------|-------------|
| user | OneToOneField(User) | Linked user account |
| subject | CharField(100) | Subject specialization |
| profile_picture | ImageField | Teacher photo (optional) |

#### ParentProfile
| Field | Type | Description |
|-------|------|-------------|
| user | OneToOneField(User) | Linked user account |
| phone | CharField(20) | Contact phone number |
| students | ManyToManyField(StudentProfile) | Associated children |

---

### 3.3 Admissions App Models

#### Applicant
| Field | Type | Description |
|-------|------|-------------|
| first_name | CharField(100) | Applicant first name |
| last_name | CharField(100) | Applicant last name |
| email | EmailField | Contact email |
| phone | CharField(20) | Contact phone |
| date_of_birth | DateField | Date of birth |
| applying_grade | CharField(20) | Grade applying for |
| previous_school | CharField(200) | Previous institution |
| statement | TextField | Personal statement |
| document | FileField | Supporting documents |
| submitted_at | DateTimeField | Submission timestamp |
| status | CharField(20) | pending/approved/rejected |

---

### 3.4 Academics App Models

#### Assignment
| Field | Type | Description |
|-------|------|-------------|
| teacher | ForeignKey(TeacherProfile) | Assigning teacher |
| title | CharField(200) | Assignment title |
| description | TextField | Assignment details |
| due_date | DateField | Submission deadline |
| created_at | DateTimeField | Creation timestamp |

#### Grade
| Field | Type | Description |
|-------|------|-------------|
| student | ForeignKey(StudentProfile) | Student being graded |
| assignment | ForeignKey(Assignment) | Related assignment |
| score | DecimalField(5,2) | Score achieved |
| remarks | TextField | Teacher comments (optional) |

#### Attendance
| Field | Type | Description |
|-------|------|-------------|
| student | ForeignKey(StudentProfile) | Student marked |
| date | DateField | Attendance date |
| status | CharField(10) | present/absent |
| recorded_by | ForeignKey(TeacherProfile) | Recording teacher |

---

### 3.5 News App Models

#### NewsPost
| Field | Type | Description |
|-------|------|-------------|
| title | CharField(200) | Article title |
| slug | SlugField | URL-friendly identifier |
| image | ImageField | Featured image |
| content | TextField | Article content |
| created_at | DateTimeField | Publication date |

---

## 4. Functionality Specification

### 4.1 Authentication System (accounts/)

#### User Registration (/accounts/register/)
- Form fields: username, email, password, role selection
- Roles: Student, Teacher, Parent
- Validates password strength
- Auto-creates user with selected role group

#### User Login (/accounts/login/)
- Email/username authentication
- Redirects based on user role
- Session management

#### User Logout (/accounts/logout/)
- Clears session data
- Redirects to home page

#### Profile Completion (/accounts/complete-profile/<role>/)
- Student: admission number, grade
- Teacher: subject specialization
- Parent: phone, linked students

#### Dashboard (/accounts/dashboard/)
- Role-based dashboard routing
- Dynamic content based on user type

### 4.2 Admin Panel (/accounts/admin_dashboard/)

#### User Management
| Feature | URL | Description |
|---------|-----|-------------|
| Users List | /accounts/users_list/ | View all registered users |
| Create User | /accounts/create-user/ | Manual user creation |
| Delete User | /accounts/users/<pk>/delete/ | Remove user account |
| Search Students | /accounts/search-students/ | Find students by name |

#### Applicant Management
| Feature | URL | Description |
|---------|-----|-------------|
| Applicants List | /accounts/applicant_list/ | View all applications |
| Applicant Detail | /accounts/applicants/<pk>/ | View application details |
| Delete Applicant | /accounts/applicants/<pk>/delete/ | Remove application |

### 4.3 Public Pages (core/)

#### Home Page (/)
- Displays school welcome message
- Shows latest 3 news posts
- Navigation to other sections

#### About Page (/about/)
- School information display
- Mission, vision, history from SchoolInfo model

#### Contact Page (/contact/)
- Static contact information page

#### Gallery Management
| Feature | URL | Description |
|---------|-----|-------------|
| View Gallery | /gallery/ | Public gallery view |
| Add Image | /gallery_create/ | Admin uploads image |
| Delete Image | /gallery/delete/<pk>/ | Admin removes image |

### 4.4 Admissions System (admissions/)

#### Online Application (/admissions/)
- Public access (no login required)
- Form fields:
  - Personal: first name, last name, DOB
  - Contact: email, phone
  - Academic: applying grade, previous school
  - Documents: personal statement, file upload
- Auto-sets status to "pending"
- Records submission timestamp

### 4.5 Academics System (academics/)

#### Teacher Functions (Requires Teacher Role)

**Create Assignment** (/academics/create/)
- Select/create assignment
- Set title, description, due date
- Auto-links to teacher profile

**Record Grades** (/academics/record-grade/)
- Select student from dropdown
- Select assignment
- Enter score and remarks
- Prevents duplicate grades

**Record Attendance** (/academics/record-attendance/)
- Select student
- Enter date and status (present/absent)
- Validates not recording future dates
- Links to recording teacher

#### Student Dashboard (/academics/student-dashboard/)
- View assigned assignments
- View personal grades
- View attendance history
- Requires completed profile

#### Teacher Dashboard (/academics/teacher-dashboard/)
- Quick stats overview
- Recent assignments created
- Quick links to create functions

#### Parent Dashboard (/academics/parent-dashboard/)
- View linked children's progress
- Assignment completion status
- Attendance records
- Academic performance

### 4.6 News System (news/)

#### Public News
| Feature | URL | Description |
|---------|-----|-------------|
| News List | /news/ | All published news |
| News Detail | /news/<slug>/ | Full article view |

#### Admin News Management
| Feature | URL | Description |
|---------|-----|-------------|
| Create Post | /news/create/ | Publish new article |
| Delete Post | /news/delete/<pk>/ | Remove article |

---

## 5. User Interface Templates

### 5.1 Base Templates
- `base.html` - Main layout with header/footer
- `base_dashboard.html` - Dashboard layout with sidebar

### 5.2 Core Templates
- `home.html` - Homepage
- `about.html` - About page
- `contact.html` - Contact page
- `gallery.html` - Image gallery
- `gallery_create.html` - Add gallery image

### 5.3 Account Templates
- `login.html` - Login form
- `register.html` - Registration form
- `dashboard.html` - Role-based dashboard
- `admin_dashboard.html` - Admin panel
- `create_user.html` - User creation form
- `complete_profile.html` - Profile setup
- `applicant_detail.html` - Application review
- `partials/` - Reusable components (sidebar, topbar, lists)

### 5.4 Academics Templates
- `student_dashboard.html` - Student view
- `teacher_dashboard.html` - Teacher view
- `parent_dashboard.html` - Parent view
- `assignment_list.html` - Assignments view
- `create_assignment.html` - Assignment form
- `record_grade.html` - Grade entry form
- `record_attendance.html` - Attendance form

### 5.5 News Templates
- `news_list.html` - News listing
- `news_detail.html` - Article view
- `news_create.html` - Article creation

### 5.6 Admissions Templates
- `apply.html` - Application form

---

## 6. User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full CRUD on all resources, user management, applicant review |
| **Teacher** | Create assignments, record grades/attendance, view own dashboard |
| **Student** | View assignments, grades, attendance, own profile |
| **Parent** | View linked children's progress |
| **Visitor** | View public pages, submit application |

---

## 7. URL Routing Summary

```
# Main URLs (config/urls.py)
/admin/                  - Django admin
/                        - Home page (core)
/about/                  - About page
/contact/                - Contact page
/gallery/                - Gallery view
/gallery_create/         - Add gallery image
/gallery/delete/<pk>/    - Delete gallery image

# News URLs
/news/                   - News list
/news/<slug>/            - News detail
/news/create/            - Create news
/news/delete/<pk>/       - Delete news

# Admissions URLs
/admissions/             - Application form

# Account URLs
/accounts/login/         - User login
/accounts/logout/        - User logout
/accounts/register/      - User registration
/accounts/dashboard/     - Main dashboard
/accounts/complete-profile/<role>/ - Profile setup
/accounts/admin_dashboard/ - Admin panel
/accounts/users_list/    - Users list
/accounts/create-user/   - Create user
/accounts/users/<pk>/delete/ - Delete user
/accounts/applicant_list/ - Applicants list
/accounts/applicants/<pk>/ - Applicant detail
/accounts/search-students/ - Search students

# Academics URLs
/academics/              - Assignment list
/academics/create/       - Create assignment
/academics/record-grade/ - Record grades
/academics/record-attendance/ - Record attendance
/academics/student-dashboard/ - Student view
/academics/teacher-dashboard/ - Teacher view
/academics/parent-dashboard/ - Parent view
```

---

## 8. Forms Specification

### 8.1 Authentication Forms
- **RegisterForm**: username, email, password1, password2, role
- **AdminCreateUserForm**: username, email, password1, password2, role, is_staff, is_superuser

### 8.2 Profile Forms
- **StudentProfileForm**: admission_number, grade, profile_picture
- **TeacherProfileForm**: subject, profile_picture
- **ParentProfileForm**: phone, students (multiple select)

### 8.3 Academic Forms
- **AssignmentForm**: title, description, due_date
- **GradeForm**: student, assignment, score, remarks
- **AttendanceForm**: student, date, status

### 8.4 News Forms
- **NewsPostForm**: title, image, content

### 8.5 Admission Forms
- **ApplicantForm**: first_name, last_name, email, phone, date_of_birth, applying_grade, previous_school, statement, document

---

## 9. Security Requirements

### 9.1 Authentication
- Password hashing via Django's PBKDF2
- Session-based authentication
- Login required decorators on protected views

### 9.2 Authorization
- Role-based access control (RBAC)
- Admin-only restrictions on sensitive operations
- Teacher-only restrictions on academic management

### 9.3 Input Validation
- Form validation on all user inputs
- CSRF protection on all POST requests
- File upload validation

---

## 10. Deployment Configuration

### 10.1 Files for Deployment
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku/Render process type
- `render.yaml` - Render deployment config
- `vercel.json` - Vercel deployment config
- `runtime.txt` - Python version specification
- `start.sh` - Startup script

### 10.2 Environment Variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode setting
- `ALLOWED_HOSTS` - Allowed host domains

---

## 11. Future Enhancements (Out of Scope)
- Email notifications
- SMS alerts
- Payment gateway integration
- Online examination system
- Library management
- Transportation tracking
- Mobile app

---

## 12. Acceptance Criteria

### 12.1 Authentication
- Users can register with role selection
- Users can login/logout
- Protected pages redirect to login

### 12.2 User Management
- Admin can view all users
- Admin can create/delete users
- Profile completion works for all roles

### 12.3 Academics
- Teachers can create assignments
- Teachers can record grades
- Teachers can mark attendance
- Students can view their data
- Parents can view linked students

### 12.4 Admissions
- Visitors can submit applications
- Admin can review applicants
- Applicant status can be updated

### 12.5 News
- Anyone can view news
- Admin can create/delete news

### 12.6 Gallery
- Anyone can view gallery
- Admin can upload/delete images

---

**Document Prepared by:** Claude Code  
**Date:** 2024
