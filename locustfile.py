from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import random
import re

class SurveyUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def enter_and_answer_survey(self):
        # Step 1: Enter the survey
        r = self.client.get("/enter/pika_nor", name="/enter/pika_nor")
        if r.status_code != 200:
            return

        # Step 2: Submit to get redirected
        r = self.client.post("/enter/pika_nor", data={"next": "1"}, allow_redirects=False, name="Submit /enter")
        if r.status_code not in (302, 303):
            return

        # Step 3: Extract token from redirect URL
        location = r.headers.get("Location", "")
        match = re.match(r"/page/([a-zA-Z0-9_-]+)", location)
        if not match:
            return
        token = match.group(1)

        # Step 4: Visit the actual question page
        r = self.client.get(f"/page/{token}", name="/page/<token>")
        if r.status_code != 200:
            return

        # Step 5: Parse the HTML to extract question fields
        soup = BeautifulSoup(r.text, "html.parser")
        form = soup.find("form", {"id": "page"})
        if not form:
            return

        data = {}

        for input_tag in form.find_all(["input", "select", "textarea"]):
            name = input_tag.get("name")
            if not name or name == "next":
                continue

            tag_type = input_tag.name
            input_type = input_tag.get("type")

            # Radio buttons: pick one per name group
            if input_type == "radio":
                if name not in data:
                    data[name] = input_tag.get("value", "0")

            # Checkboxes: multiple allowed, simulate random subset
            elif input_type == "checkbox":
                if random.random() < 0.5:
                    if name not in data:
                        data[name] = []
                    data[name].append(input_tag.get("value", "0"))

            # Hidden fields: typically question metadata (type, key)
            elif input_type == "hidden":
                data[name] = input_tag.get("value", "")

            # Range: set to middle value
            elif input_type == "range":
                min_val = int(input_tag.get("min", 0))
                max_val = int(input_tag.get("max", 10))
                data[name] = str((min_val + max_val) // 2)

            # Number fields
            elif input_type == "number":
                data[name] = str(random.randint(1, 5))

            # Text fields
            elif input_type == "text":
                data[name] = "example"

            # Textarea
            elif tag_type == "textarea":
                data[name] = "multiline answer"

            # Select dropdowns
            elif tag_type == "select":
                options = input_tag.find_all("option")
                valid_options = [opt.get("value") for opt in options if opt.get("value")]
                if valid_options:
                    data[name] = random.choice(valid_options)

        # Flatten multi-checkbox values
        flat_data = {}
        for k, v in data.items():
            if isinstance(v, list):
                for val in v:
                    flat_data[k] = val  # will only submit one; can use tuple format if backend supports it
            else:
                flat_data[k] = v

        # Add "next" hidden input
        flat_data["next"] = "1"

        # Step 6: Post the answer
        self.client.post(f"/page/{token}", data=flat_data, name="Answer /page/<token>")
