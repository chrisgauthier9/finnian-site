/* Mailing-list signup, posting straight to EmailOctopus.

   The form endpoint answers an ordinary CORS fetch from finnian.ca and returns
   JSON, so the response can be read. That matters: it replies
   {"error":{"code":...,"message":...}} with a 400 for a rejected address, and
   without reading it the form would claim success for everything. It did exactly
   that once already, under MailerLite.

   Account "Finnian", list 105c4204-ac94-11f1-823e-83f2f4d0cb84, form "finnian.ca signup".
   `field_0` is EmailOctopus's name for the email input. The long `hp...` field is
   their honeypot and must be sent empty: it is the only bot protection on this form,
   because the hidden reCAPTCHA is off (it cannot work from our own markup).
   Contacts land as SUBSCRIBED immediately; there is no double opt-in step. */

const SIGNUP_ENDPOINT = "https://eomail5.com/form/61b0d18c-ad9e-11f1-9638-2b2cb9b136b2";
const HONEYPOT_FIELD = "hpc4b27b6e-eb38-11e9-be00-06b4694bee2a";
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
    body.append("field_0", email);
    body.append(HONEYPOT_FIELD, "");

    try {
      const response = await fetch(SIGNUP_ENDPOINT, {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        body,
      });
      const result = await response.json();

      if (response.ok && result && result.success) {
        form.reset();
        say("You are on the list. Check your inbox.");
        return;
      }

      // Their wording is generic ("This form has missing or invalid fields"),
      // so say the useful thing instead and keep the fallback address visible.
      say(`That address was not accepted. Try again, or email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    } catch (error) {
      say(`Something went wrong. Email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    }
  });
});
