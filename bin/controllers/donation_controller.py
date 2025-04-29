from bin.response.response_model import ResponseModel,ErrorResponseModel
from bin.services.db_services.donation_service import create_new_donation_record,currency_list,donation_list,sum_of_donations

class DonationManager():
    def donation(self,request):
        try:
            create_new_donation_record(request)
            return ResponseModel(request,"Succesfully created new donation")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    def get_currency_list(self):
        try:
            currency = currency_list()
            return ResponseModel(currency,'All currency list')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    def donation_types(self):
        try:
            donations = donation_list()
            return ResponseModel(donations, 'All donation types')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    def get_total_donations(self):
        try:
            total_donation = sum_of_donations()

            return ResponseModel(total_donation,'sum of general donations')

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

donationManager = DonationManager()