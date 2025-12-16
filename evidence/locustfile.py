# from locust import HttpUser, TaskSet, task, events

# class WebsiteTasks(TaskSet):
#     @task
#     def load_test(self):
#         response = self.client.get("/")
#         if response.status_code != 200:
#             global failed_requests
#             failed_requests += 1

# class WebsiteUser(HttpUser):
#     tasks = [WebsiteTasks]
#     min_wait = 100
#     max_wait = 500
#     host = "http://testphp.vulnweb.com"

# # Global counters
# total_requests = 0
# failed_requests = 0

# @events.request.add_listener
# def on_request_complete(request_type, name, response_time, response_length, response, **kwargs):
#     global total_requests
#     total_requests += 1

# @events.quitting.add_listener
# def on_quit():
#     failed_percentage = (failed_requests / total_requests * 100) if total_requests else 0
#     requests_per_second = total_requests / 60  # Assuming 1-minute test
#     print("\n===== Test Summary =====")
#     print(f"Total Requests Sent: {total_requests}")
#     print(f"Failed Requests: {failed_requests}")
#     print(f"Failure Percentage: {failed_percentage:.2f}%")
#     print(f"Requests Per Second: {requests_per_second:.2f}")

# if __name__ == "__main__":
#     import os
#     os.system("locust --headless -u 5000 -r 500 -t 1m")



import requests


while True:
    r = requests.get("https://uatmis.nirmauni.ac.in/Login.aspx")
    print(r.status_code)