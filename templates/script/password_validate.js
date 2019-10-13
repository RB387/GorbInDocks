function validatePassword(){
	var password = document.getElementById("pass")
	, confirm_password = document.getElementById("pass_conf");
	if(password.value != confirm_password.value) {
		confirm_password.setCustomValidity("Passwords Don't Match");
	} else {
		confirm_password.setCustomValidity('');
	}
}
