from datetime import datetime
from db.models import Issue, IssueState
from metrics.sqlite_query import SQLiteQuery
from metrics.metrics import Metrics
from redmine.redmine_dumper import RedmineStatus


def test_count_status():
    query = SQLiteQuery(":memory:")
    session = query.session

    date_on_new = datetime(2023, 1, 1)
    date_move_on_resolved = datetime(2023, 2, 1)

    # 1 new, 1 workable, 2 in progress, 1 resolved
    session.add(
        Issue(
            {'issue_id': 1,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.NEW.value,
             'created_on': date_on_new}
        )
    )
    session.add(
        Issue(
            {'issue_id': 2,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.WORKABLE.value,
             'created_on': date_on_new}
        )
    )
    session.add(
        Issue(
            {'issue_id': 3,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.IN_PROGRESS.value,
             'created_on': date_on_new}
        )
    )
    session.add(
        Issue(
            {'issue_id': 4,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.IN_PROGRESS.value,
             'created_on': date_on_new}
        )
    )
    session.add(
        Issue(
            {'issue_id': 5,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.RESOLVED.value,
             'created_on': date_on_new,
             'closed_on': date_move_on_resolved, }
        )
    )
    session.commit()

    metrics = Metrics(query)
    status_counters = metrics.status_count()
    assert status_counters[RedmineStatus.NEW] == 1
    assert status_counters[RedmineStatus.WORKABLE] == 1
    assert status_counters[RedmineStatus.IN_PROGRESS] == 2
    assert status_counters[RedmineStatus.RESOLVED] == 1

    session.close()


def test_status_count_by_date():
    query = SQLiteQuery(":memory:")
    session = query.session

    date_on_new = '2023-01-01'
    date_on_in_progress_1 = '2023-01-10'
    date_on_in_progress_2 = '2023-01-15'
    date_move_on_resolved = '2023-02-01'

    # Issue 1
    session.add(
        Issue(
            {'issue_id': 1,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.NEW.value,
             'created_on': date_on_new}
        )
    )
    # Issue 2
    session.add(
        Issue(
            {'issue_id': 2,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.IN_PROGRESS.value,
             'created_on': date_on_new}
        )
    )
    session.add(
        IssueState(
            issue_id=2,
            field="status",
            created_on=date_on_new,
            new_value=RedmineStatus.NEW.value
        )
    )
    session.add(
        IssueState(
            issue_id=2,
            field="status",
            created_on=date_on_in_progress_2,
            new_value=RedmineStatus.IN_PROGRESS.value
        )
    )
    # Issue 3
    session.add(
        Issue(
            {'issue_id': 3,
             'project_id': 1,
             'type_id': 1,
             'status_id': RedmineStatus.RESOLVED.value,
             'created_on': date_on_new,
             'closed_on': date_move_on_resolved}
        )
    )
    session.add(
        IssueState(
            issue_id=3,
            field="status",
            created_on=date_on_in_progress_1,
            new_value=RedmineStatus.IN_PROGRESS.value
        )
    )
    session.add(
        IssueState(
            issue_id=3,
            field="status",
            created_on=date_move_on_resolved,
            new_value=RedmineStatus.RESOLVED.value
        )
    )
    session.commit()

    metrics = Metrics(query)
    status_counters = metrics.status_count_by_date(date_on_in_progress_2)
    assert status_counters[RedmineStatus.NEW] == 1
    assert status_counters[RedmineStatus.IN_PROGRESS] == 2
    assert RedmineStatus.RESOLVED not in status_counters

    session.close()
