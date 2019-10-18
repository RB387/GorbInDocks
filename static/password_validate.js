function validatePassword(){
		var password = document.getElementById("pass")
		, confirm_password = document.getElementById("pass_conf");
		if(password.value != confirm_password.value) {
				confirm_password.setCustomValidity("Passwords doesn't match");
		} else {
				confirm_password.setCustomValidity('');
		}
}