from google.genai import errors as genai_errors
from rag_core import conn, cur
from rag_safe import answer_question_safe, with_retry, InvalidQuestion, ServiceError


class FakeAPIError(genai_errors.APIError):
    """Simulated Gemini error with a chosen HTTP status code."""
    def __init__(self, code):
        Exception.__init__(self, f"{code} simulated")
        self.code = code


def try_ask(label, q):
    print(f"\n--- {label} ---")
    try:
        print(answer_question_safe(q))
    except InvalidQuestion as e:
        print("InvalidQuestion:", e)
    except ServiceError as e:
        print("ServiceError:", e)


try_ask("empty", "")
try_ask("spaces only", "     ")
try_ask("punctuation only", "?!?!")
try_ask("too long", "a" * 5000)
try_ask("gibberish", "asdkjh qweoiu zxcmnb")
try_ask("normal question", "Name the four Galilean moons.")

# Empty table: delete inside a transaction, test, then roll back so nothing is lost
cur.execute("DELETE FROM document")
try_ask("empty table", "Name the four Galilean moons.")
conn.rollback()
cur.execute("SELECT count(*) FROM document")
print("\nRows restored after rollback:", cur.fetchone()[0])

# Retry: fails twice with 503, succeeds on the third try (takes about 3 seconds)
calls = {"n": 0}
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise FakeAPIError(503)
    return "recovered"
print("\n", with_retry(flaky), "after", calls["n"], "tries")

# Non-retryable error (400): should fail immediately, with no waiting
def bad_request():
    raise FakeAPIError(400)
try:
    with_retry(bad_request)
except ServiceError as e:
    print("Failed immediately:", e)