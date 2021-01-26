# Open Access Membership Signup
"otf" is a generic signup system for open-access projects that have [consortial membership models](https://doi.org/10.7710/2162-3309.1131).

This system allows OA publishers with membership schemes (such as [Opening the Future](https://openingthefuture.net/) or the [Open Library of Humanities](https://openlibhums.org/plugins/supporters/signup/)) to collect and process library signups.

Features include:

* Order tracking
* Billing managers on a per-country basis
* Email notifications on a per-country basis
* Access control CSV generation for back-content access (as in Opening the Future)

"otf" is developed by the Birkbeck Centre for Technology and Publishing and was part of the [COPIM project](https://www.copim.ac.uk/). Special thanks go to Andy Byers for his work on the platform.


# Development
To work on this code we recommend you use Docker, clone the repository and in the root directory run:

`make install` to setup

and

`make run` to run the Django webserver.
