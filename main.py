from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, date, timedelta
from fastapi.responses import HTMLResponse
from database import engine, SessionLocal
from fastapi.staticfiles import StaticFiles

from models import (
    Base,
    Category,
    ActiveSession,
    SessionHistory,
    AppSettings
)

Base.metadata.create_all(bind=engine)

app = FastAPI()
pending_session = {}

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
@app.get("/")
def home(
    request: Request,
    filter: str = "today"
):

    db = SessionLocal()

    categories = db.query(
        Category
    ).all()

    active_session = db.query(
        ActiveSession
    ).first()

    settings = db.query(
        AppSettings
    ).first()

    if not settings:

        settings = AppSettings(
            daily_goal=8
        )

        db.add(settings)

        db.commit()

    today = date.today()

    if filter == "today":

        target = today.strftime("%Y-%m-%d")

        history = db.query(
            SessionHistory
        ).filter(
            SessionHistory.session_date == target
        ).all()

    elif filter == "yesterday":

        target = (
            today - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        history = db.query(
            SessionHistory
        ).filter(
            SessionHistory.session_date == target
        ).all()

    elif filter == "week":

        week_start = (
            today - timedelta(days=7)
        )

        history = db.query(
            SessionHistory
        ).all()

        history = [
            h
            for h in history
            if datetime.strptime(
                h.session_date,
                "%Y-%m-%d"
            ).date() >= week_start
        ]

    else:

        history = db.query(
            SessionHistory
        ).all()

    daily_total = sum(
        h.duration
        for h in history
    )

    session_count = len(history)

    longest_session = max(
        [h.duration for h in history],
        default=0
    )

    categories_used = len(
        set(
            h.category
            for h in history
        )
    )
    
    all_sessions = db.query(
        SessionHistory
    ).all()

    study_dates = sorted(
        list(
            set(
                datetime.strptime(
                    s.session_date,
                    "%Y-%m-%d"
                ).date()
                for s in all_sessions
            )
        )
    )

    current_streak = 0
    best_streak = 0

    if study_dates:

        streak = 1

        for i in range(
            1,
            len(study_dates)
        ):

            if (
                study_dates[i]
                -
                study_dates[i - 1]
            ).days == 1:

                streak += 1

            else:

                best_streak = max(
                    best_streak,
                    streak
                )

                streak = 1

        best_streak = max(
            best_streak,
            streak
        )

        temp_date = date.today()

        while temp_date in study_dates:

            current_streak += 1

            temp_date -= timedelta(
                days=1
            )
                    
    weekly_categories = {}

    for item in history:

        if item.category not in weekly_categories:

                weekly_categories[item.category] = 0

        weekly_categories[item.category] += item.duration

    total_hours = sum(
        s.duration
        for s in all_sessions
    ) // 3600

    achievements = []

    if len(all_sessions) >= 1:
            achievements.append(
                "🏆 First Session"
            )

    if total_hours >= 10:
            achievements.append(
                "⏱ 10 Hours Logged"
            )

    if current_streak >= 7:
            achievements.append(
                "🔥 7 Day Streak"
            )

    if len(all_sessions) >= 100:
            achievements.append(
                "🚀 100 Sessions"
            )

    
    # TEMPORARY TEST VALUES


    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "categories": categories,
            "active_session": active_session,
            "history": history,
            "daily_total": daily_total,
            "goal": settings.daily_goal,
            "session_count": session_count,
            "longest_session": longest_session,
            "categories_used": categories_used,
            "filter": filter,
            "weekly_categories": weekly_categories,
            "achievements": achievements,

            # STREAKS
            "current_streak": current_streak,
            "best_streak": best_streak
        }
    )

@app.post("/add-category")
def add_category(subject_name: str = Form(...)):

    db = SessionLocal()

    new_category = Category(
        name=subject_name
    )

    db.add(new_category)

    db.commit()

    db.close()

    return RedirectResponse(
        "/",
        status_code=303
    )
@app.post("/save-goal")
def save_goal(
    goal: int = Form(...)
):

    db = SessionLocal()

    settings = db.query(
        AppSettings
    ).first()

    if settings:

        settings.daily_goal = goal

    else:

        settings = AppSettings(
            daily_goal=goal
        )

        db.add(settings)

    db.commit()

    db.close()

    return RedirectResponse(
        "/",
        status_code=303
    )

@app.post("/start-session")
def start_session(
    category: str = Form(...),
    task: str = Form(...)
):

    db = SessionLocal()

    existing = db.query(
        ActiveSession
    ).first()

    if existing:

        db.close()

        return RedirectResponse(
            "/",
            status_code=303
        )

    session = ActiveSession(
        category=category,
        task=task,
        start_time=datetime.now(),
        is_running=True
    )

    db.add(session)

    db.commit()

    db.close()

    return RedirectResponse(
        "/",
        status_code=303
    )


@app.post("/stop-session")
def stop_session(request: Request):

    global pending_session

    db = SessionLocal()

    active = db.query(
        ActiveSession
    ).first()

    if active:

        pending_session = {

            "category": active.category,

            "task": active.task,

            "start_time": active.start_time,

            "end_time": datetime.now()

        }

        db.delete(active)

        db.commit()

    db.close()
    return templates.TemplateResponse(
        request=request,
        name="add_notes.html",
        context={}
    )

@app.post("/save-session")
def save_session(
    notes: str = Form("")
):

    global pending_session

    db = SessionLocal()

    duration = int(

        (
            pending_session["end_time"]
            -
            pending_session["start_time"]
        ).total_seconds()

    )

    history = SessionHistory(

        category=
        pending_session["category"],

        task=
        pending_session["task"],

        start_time=
        pending_session["start_time"],

        end_time=
        pending_session["end_time"],

        duration=
        duration,

        session_date=
        pending_session[
            "end_time"
        ].strftime(
            "%Y-%m-%d"
        ),

        notes=notes

    )

    db.add(history)

    db.commit()

    db.close()

    pending_session = {}

    return RedirectResponse(
        "/",
        status_code=303
    )

@app.post("/delete-category/{category_id}")
def delete_category(category_id: int):

    db = SessionLocal()

    category = db.query(
        Category
    ).filter(
        Category.id == category_id
    ).first()

    if category:
        db.delete(category)
        db.commit()

    db.close()

    return RedirectResponse(
        "/",
        status_code=303
    )

@app.get("/tv")
def tv_dashboard(request: Request):

    db = SessionLocal()

    active_session = db.query(
        ActiveSession
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="tv.html",
        context={
            "active_session": active_session
        }
    )