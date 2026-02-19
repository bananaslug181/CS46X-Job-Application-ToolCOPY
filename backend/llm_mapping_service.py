from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json
import os
import time
import encryption_service
import base64
import logging
from openai import OpenAI
import google.genai as genai
from tests.test_heuristic_matcher import HeuristicMatcher # import heuristic class (from testing frame)

# Credit to Gemini for assistance with writing

class FormInteractionEngine:
    def __init__(self, driver_path=None):
        self.driver = webdriver.Chrome()
        self.matcher = HeuristicMatcher()
        self.found_elements = []

    def getDecryptedData(self, encrypted_data):
        # decrypt the file so the values in users file can be correctly placed into form based on heuristic service
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(BASE_DIR, 'encryption.key')
            decrypted_profile = encryption_service.decrypt_profile_simple(encrypted_data, key_path)
            return decrypted_profile
        except Exception as e:
            print(f"Failed to decrypt profile: {e}")
            return

    def load_test_page(self, url: str):
        """Navigates to local server e.g., http://127.0.0.1:8001 """
        self.driver.get(url)

    def get_fields(self):
        """TO BE REPLACED WITH GARETHS PROGRAM"""

        try:
            tags = ["input", "select", "textarea", "button"]

            # for each tag, find all the elements in the page for that tag and extract each elements data
            for tag in tags:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for el in elements:
                    field_id = el.get_attribute("id")
                    field_name = el.get_attribute("name")
                    identifier = field_id or field_name or f"{tag}_{elements.index(el)}" # in case is unknown
                    metadata = {
                        "tag": tag,
                        "type": el.get_attribute("type") or "text",
                        "id": identifier,
                        "name": el.get_attribute("name"),
                        "placeholder": el.get_attribute("placeholder"),
                        "label_text": self._find_label(el),
                        "aria_label": el.get_attribute("aria-label")
                    }

                    if tag == "select":
                        # Scrape all the text from the option tags
                        select_obj = Select(el)
                        # skip the "please select an option" placeholder
                        options = [o.text for o in select_obj.options if "select" not in o.text.lower()]
                        metadata["options"] = options

                    # add metadata
                    self.found_elements.append(metadata)

            return self.found_elements
        except Exception as e:
            return False

    def _find_label(self, element):
        """Finds the label of an element"""
        element_id = element.get_attribute("id")
        if element_id:
            try:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{element_id}']")
                return label.text
            except:
                pass

        # Check for aria-label
        aria_label = element.get_attribute("aria-label")
        if aria_label: return aria_label

        # fallback to check parent element text
        try:
            return element.find_element(By.XPATH, "..").text.split("\n")[0]
        except: return ""

    def fill_form_from_profile(self, profile_data):
        unknown_elements = []
        results = []

        print(f"DEBUG: Starting fill for {len(self.found_elements)} elements...")

        for element_metadata in self.found_elements:
            # 1. Check the Matcher
            backend_key = self.matcher.get_best_match(element_metadata)
            print(f"DEBUG: Field '{element_metadata.get('id')}' matched to: {backend_key}")

            if backend_key == 'unknown':
                unknown_elements.append(element_metadata)
            else:
                value_to_input = profile_data.get(backend_key)
                if value_to_input:
                    print(f"DEBUG: Heuristic Match found! Filling {backend_key}...")
                    res = self.execute_fill(value_to_input, element_metadata['id'], backend_key)
                    results.append(res)

        # 2. Check the AI Phase
        if unknown_elements:
            print(f"DEBUG: Sending {len(unknown_elements)} items to Gemini...")
            try:
                llm_results = self.ai_helper(unknown_elements, profile_data)
                print(f"DEBUG: Gemini Response: {llm_results}")

                for field_id, value in llm_results.items():
                    if value and value != "N/A":
                        result = self.execute_fill(value, field_id, "AI_Mapping")
                        results.append(result)
            except Exception as e:
                print(f"DEBUG: AI Phase CRASHED: {e}")

        print(f"DEBUG: fill_form_from_profile returning {len(results)} results.")
        return results

    def ai_helper(self, unknown_elements, profile_data):

        client = genai.Client(api_key="AIzaSyAoXnu6g37UD5Ym4SJbyPWNFVCfaVIIGoo")

        prompt = f"""Your goal is to assist in a job application process by matching the correct profile data to
        a list of unknown elements. Return a JSON object where the keys are the 'id' of the field and the values are the corresponding
        data from the candidate profile.

        RULES:
        1. For 'select' (dropdown) fields, you must choose exactly one string from the 'options' list provided.
        2. If a field doesn't have an exact match in the profile, infer the most logical answer from the profile data.
        3. Choose the 'options' string that best represents the candidate's background.
        4. If it is impossible to determine an answer, return "N/A", except for dropdowns, then choose whichever makes the most sense.

        FIELDS TO FILL: {unknown_elements}
        PROFILE DATA: {profile_data}
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config={
                'response_mime_type': 'application/json' # make it actually make a JSON file
            }
        )
        return json.loads(response.text)


    def execute_fill(self, value_to_input, element_id, backend_key):
        try:
            wait = WebDriverWait(self.driver, 10)
            target = wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            # Handle Dropdowns vs Text Inputs
            if target.tag_name == "select":
                Select(target).select_by_visible_text(str(value_to_input))
            else:
                target.clear()
                target.send_keys(str(value_to_input))

            return({"field": backend_key, "status": "SUCCESS"})
        except Exception as e:
            return({"field": backend_key, "status": "FAILED", "error": str(e)})


    def save_logs(self, results, filename="interaction_log.json"):
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Logs from webdriver saved to: {filename}")


def main():
    engine = FormInteractionEngine()
    template_id = "mackay_sposito"
    base_url = f"https://the-internet.herokuapp.com/checkboxes"
    encrypted_profile = 'backend/encrypted_profile.json'
    #base_url = f"http://127.0.0.1:8001/apply/{template_id}"

    try:
        # open the encrypted user file
        with open(encrypted_profile, 'r') as f:
            encrypted_data = json.load(f)

        # decrypt the file
        decrypted_user_data = engine.getDecryptedData(encrypted_data)
        if not decrypted_user_data:
            print("ERROR: Could not decrypt data.\n")
            return

        print(f"Testing Template: {template_id} at {base_url}\n")

        # Load the page via the server URL
        print(f"Connecting to: {base_url}")
        engine.driver.get(base_url)
        # clear the old elements before scanning the new page
        engine.found_elements = []
        # use the webdriver to get the fields that need to be filled
        engine.get_fields()


        print(f"DEBUG: Scanned the page. Found {len(engine.found_elements)} elements.")
        for el in engine.found_elements:
            print(f"  - Found {el['tag']} with ID: {el['id']}")

        # put that decrypted user data into the fields
        page_results = engine.fill_form_from_profile(decrypted_user_data['applicant_info'])
        print(f"DEBUG: Interaction complete. Results count: {len(page_results)}")

        engine.save_logs({template_id: page_results}, "full_test_logs.json")
        time.sleep(2)

    finally:
        engine.driver.quit()


if __name__ == "__main__":
    main()
