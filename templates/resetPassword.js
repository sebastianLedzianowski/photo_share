document.addEventListener("DOMContentLoaded", async function() {
    const form = document.getElementById('resetPasswordForm');
    form.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = new URLSearchParams();
        for (const pair of formData) {
            data.append(pair[0], pair[1]);
        }

        const token = document.body.getAttribute('data-token');

        try {
            const response = await fetch(`/api/auth/reset_password/${token}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: data,
            });

            if (!response.ok) {
                throw new Error('Something went wrong');
            }

            const result = await response.json();
            console.log('Password reset successfully:', result);
            window.location.href = 'base.html';
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('error-container').textContent = 'Failed to reset password.';
        }
    };
});
