/* Mailing-list signup, posting straight to MailerLite.

   The endpoint is MailerLite's JSONP form handler, which sends no CORS headers,
   so the response cannot be read from the browser. The request itself still goes
   through, so this posts with mode "no-cors" and treats completion as success.
   That means a duplicate or rejected address looks the same as a good one here;
   the truth is in the MailerLite dashboard.

   Account 2626131, form "finnian.ca signup", group "Website signups". */

const SIGNUP_ENDPOINT = "https://assets.mailerlite.com/jsonp/2626131/forms/198162648361075997/subscribe";
const FALLBACK_ADDRESS = "contact@finnian.ca";

document.querySelectorAll("[data-signup]").forEach((form) => {
  const status = form.querySelector("[data-status]");
  const input = form.querySelector('input[type="email"]');
  const button = form.querySelector('button[type="submit"]');

  const say = (message) => { if (status) status.textContent = message; };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = input.value.trim();
    if (!email || !input.checkValidity()) {
      say("That does not look like an email address.");
      input.focus();
      return;
    }

    if (!SIGNUP_ENDPOINT) {
      const subject = encodeURIComponent("Add me to the list");
      const body = encodeURIComponent(`Please add ${email} to the Finnian mailing list.`);
      window.location.href = `mailto:${FALLBACK_ADDRESS}?subject=${subject}&body=${body}`;
      say("Opening your mail app.");
      return;
    }

    button.disabled = true;
    say("One moment.");

    const body = new FormData();
    body.append("fields[email]", email);
    body.append("ml-submit", "1");
    body.append("anticsrf", "true");

    try {
      await fetch(SIGNUP_ENDPOINT, { method: "POST", mode: "no-cors", body });
      form.reset();
      say("You are on the list. Check your inbox.");
    } catch (error) {
      say(`Something went wrong. Email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    }
  });
});
