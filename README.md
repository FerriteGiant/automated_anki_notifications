## Automated Anki Notifications

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Setup</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>

  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a script intended to by run as a cronjob which will check [Ankiweb](https://ankiweb.net) to see if you have any pending card reviews and, if so, send a push notification to your phone using IFTTT.


<!-- GETTING STARTED -->
## Getting Started

Clone the project to a computer you plan to always have running and on which you can create cronjobs. I'm using a linode server running Ubuntu.

### Prerequisites

* Python 3.5 or higher
	* Python `requests` library (https://realpython.com/python-requests/)
	* Python `BeautifulSoup` library (https://www.crummy.com/software/BeautifulSoup/)
	* Python `PyYAML` library (https://pyyaml.org/wiki/PyYAMLDocumentation)
* An account on [ankiweb.net](https://ankiweb.net/)
	* At least one deck created
* A free-tier [IFTTT account](https://ifttt.com/home)

### Setup

1. Enter your ankiweb credentials into the `config_params.yaml` file
2. Set up a webhooks endpoint on IFTTT (follow [this tutorial](https://anthscomputercave.com/tutorials/ifttt/using_ifttt_web_request_email.html), except choose Notification for the action service instead of email, unless of course you want an email).
3. Fill in the event name and the event key in the `config_params.yaml` file.



<!-- USAGE EXAMPLES -->
## Usage

\<\<Fill this in with info about setting up a cronjob\>\>




<!-- CONTRIBUTING -->
## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

