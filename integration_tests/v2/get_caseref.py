import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)


def login_to_sirius(url, username, password):
    print("Logging into Sirius...")

    driver.get(url)

    username_box = driver.find_element_by_name("email")
    username_box.clear()
    username_box.send_keys(username)

    password_box = driver.find_element_by_name("password")
    password_box.clear()
    password_box.send_keys(password)

    submit_button = driver.find_element_by_name("submit")
    submit_button.click()


def search_for_caseref(url, caseref):
    print(f"Searching for caseref: {caseref}")
    driver.implicitly_wait(30)
    driver.get(f"{url}/supervision/#/search/" f"{caseref}")

    search_results = driver.find_element_by_class_name("search-results__found").text

    if "No results could be found" in search_results:
        print(f"This caseref does not exist in Sirius: {caseref}")
        return False
    else:
        print(f"This caseref does exist in Sirius: {caseref}")
        return True


def create_client(url, caseref):
    print(f"Creating client with caseref: {caseref}")
    driver.implicitly_wait(30)
    driver.get(f"{url}/supervision/#/clients/create")
    court_ref_box = driver.find_element_by_name("courtReference")
    first_name_box = driver.find_element_by_name("firstName")
    last_name_box = driver.find_element_by_name("lastName")
    submit_button = driver.find_element_by_xpath(
        "//button[contains(text()," "'Save & exit')]"
    )

    court_ref_box.send_keys(caseref)
    first_name_box.send_keys("Docs API")
    last_name_box.send_keys("Test User")

    submit_button.click()

    driver.implicitly_wait(30)
    check_it_created = (
        True
        if driver.find_element_by_class_name(
            "court-reference-value-in-client-summary"
        ).text
        == caseref
        else False
    )

    if check_it_created:
        print(f"Client created with caseref: {caseref}")
    else:
        print("Unable to create client")


@click.command()
@click.option("--caseref", prompt="Caseref you want to test with", default="86622299")
@click.option(
    "--url", default="https://frontend-dev.dev.sirius.opg.digital", prompt="Sirius URL"
)
@click.option(
    "--username", prompt="Sirius username", default="case.manager@opgtest.com"
)
@click.option("--password", prompt="Sirius password", hide_input=True)
def validate_caseref(caseref, url, username, password):

    try:
        login_to_sirius(url=url, username=username, password=password)
    except Exception as e:
        driver.quit()
        print(f"Unable to log in to Sirius: {e}")
        return f"Unable to log in to Sirius: {e}"

    caseref_exists = search_for_caseref(url=url, caseref=caseref)

    if not caseref_exists:
        create_client(url=url, caseref=caseref)

    driver.quit()

    return caseref


if __name__ == "__main__":
    validate_caseref()
