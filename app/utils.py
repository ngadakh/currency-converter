from os.path import join
import requests
from werkzeug.utils import secure_filename


def save_file_locally(form, app):
    """Save file to appropriate location"""
    try:
        file_obj = form.profile_photo.data
        filename = secure_filename(file_obj.filename)
        profile_photo_filename = str(form.username.data) + "_" + filename
        profile_photo_full_path = join(app.config['FILE_UPLOAD_PATH'], profile_photo_filename)
        file_obj.save(profile_photo_full_path)
        return True, profile_photo_filename
    except Exception as e:
        app.logger.error("Error while saving file to location {}".format(profile_photo_filename), e)
        return False, e

class CurrencyConverter():
    """This class has all function related to currency converter"""
    def __init__(self, app) -> None:
        self.app = app

    def get_all_currencies(self):
        """This function use to fetch all existing currencies from EXCHANGE_RATE_API"""
        choices = list()
        try:
            # Use USD as base currency
            response = requests.get(self.app.config["EXCHANGE_RATE_API"])
            data = response.json()
            choices.append(list(zip(data["conversion_rates"].keys(), data["conversion_rates"].keys())))
        except requests.exceptions.RequestException as err:
            self.app.logger.error("RequestException", err)
        except requests.exceptions.HTTPError as errh:
            self.app.logger.error("HTTPError", errh)
        except requests.exceptions.ConnectionError as errc:
            self.app.logger.error("ConnectionError", errc)
        except requests.exceptions.Timeout as errt:
            self.app.logger.error("Timeout", errt)
        except Exception as e:
            self.app.logger.error("Error while getting all currencies", e)

        return choices[0]
