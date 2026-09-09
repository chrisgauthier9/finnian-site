/* Mailing-list signup, posting straight to MailerLite.

   The endpoint sends `access-control-allow-origin: *`, so this is an ordinary
   CORS fetch and the JSON response can be read. That matters: MailerLite answers
   {"success":false,"errors":{...}} for a rejected address, and without reading it
   the form would claim success for everything.

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

    button.disabled = true;
    say("One moment.");

    const body = new FormData();
    body.append("fields[email]", email);
    body.append("ml-submit", "1");
    body.append("anticsrf", "true");

    try {
      const response = await fetch(SIGNUP_ENDPOINT, { method: "POST", body });
      const result = await response.json();

      if (result && result.success) {
        form.reset();
        say("You are on the list. Check your inbox.");
        return;
      }

      // Surface MailerLite's own wording rather than a generic failure.
      const fields = (result && result.errors && result.errors.fields) || {};
      const first = Object.values(fields).flat()[0];
      say(first || `Something went wrong. Email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    } catch (error) {
      say(`Something went wrong. Email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    }
  });
});
