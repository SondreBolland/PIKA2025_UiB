function findElem(name) {
	var e = document.getElementsByName(name);
	if (e)
		return e[0];
	else
		return undefined;
}

function validateOptionText(key, index, checked) {
	var elem = findElem(key + "_text_" + index);
	if (elem === undefined)
		return false;

	var error = document.getElementById("error_" + key + "_text_" + index);

	if (checked && elem.value === "") {
		error.innerText = document.errors.text || "Please enter some text";
		error.style.display = "block";
		return true;
	} else {
		error.style.display = "none";
		return false;
	}
}

function validateOptions(key) {
	var elems = document.getElementsByName(key);
	var ok = false;
	var errors = false;
	for (var i = 0; i < elems.length; i++) {
		if (elems[i].checked)
			ok = true;
		if (validateOptionText(key, i, elems[i].checked))
			errors = true;
	}

	if (!ok)
		return document.errors.options || "Please pick an option";
	else if (errors)
		return true;
	else
		return false;
}

function validateOptionsList(key) {
	var elem = document.getElementsByName(key)[0];
	if (elem.value == "")
		return document.errors.options || "Please pick an option";
	else
		return false;
}

function validateOptionsMulti(key) {
	var elems = document.getElementsByName(key);
	var ok = false;
	var errors = false;
	for (var i = 0; i < elems.length; i++) {
		if (elems[i].checked)
			ok = true;
		if (validateOptionText(key, i, elems[i].checked))
			errors = false;
	}
	if (!ok)
		return document.errors.options || "Please pick an option";
	else if (errors)
		return true;
	else
		return false;
}

function validateNumber(key) {
	var elem = document.getElementsByName(key)[0];
	var re = /^[0-9]+$/;
	if (!re.test(elem.value))
		return document.errors.number || "Please enter a number";
	return false;
}

function validateText(key) {
	var elem = document.getElementsByName(key)[0];
	if (elem.value === "")
		return document.errors.text || "Please enter some text";
	return false;
}

function validateOptionalText(key) {
	return false;
}

function validateRange(key) {
	// Nothing to validate.
	return false;
}

function validateValue(key) {
	var elem = document.getElementsByName(key)[0];
	var type = elem.value;

	if (!type) {
		return document.errors.no_value || "Please select a type!";
	}

	var inputElem = document.getElementsByName(key + "_val")[0];
	var text = inputElem.value;

	var info = document.value_types[type];
	if (info) {
		var re = new RegExp("^" + info.validate + "$");
		if (!re.test(text)) {
			return document.errors.value[type] || "Please check your value!";
		}
	}

	return false;
}

function validateType(key) {
	var elem = document.getElementsByName(key)[0];
	if (!elem.value)
		return document.errors.options || "Please pick an option";
	else
		return false;
}

function validateMultiLineText(key) {
	var checkbox = document.getElementById(key + "_idk");
	if (checkbox && checkbox.checked) {
		return false;
	}
	var elem = document.getElementsByName(key)[0];
	if (elem.value.trim() === "") {
		return document.errors.text || "Please enter some text";
	}
	return false;
}


function toggleTextArea(key) {
	var checkbox = document.getElementById(key + "_idk");
	var textarea = document.getElementById(key);
	if (checkbox.checked) {
		textarea.disabled = true;
		textarea.classList.add("disabled");
		textarea.value = "";
		document.getElementById("error_" + key).style.display = "none";
	} else {
		textarea.disabled = false;
		textarea.classList.remove("disabled");
	}
}

function validate() {
	var types = {
		"options": validateOptions,
		"options-list": validateOptionsList,
		"options-multi": validateOptionsMulti,
		"number": validateNumber,
		"text": validateText,
		"optional_text": validateOptionalText,
		"range": validateRange,
		"value": validateValue,
		"type": validateType,
		"multi_line_text": validateMultiLineText
	};
	var ok = true;

	for (var i = 0; ; i++) {
		var type = findElem("type_" + i);
		var key = findElem("key_" + i);

		if (!type || !key)
			break;

		type = type.value;
		key = key.value;

		if (types.hasOwnProperty(type)) {
			var msg = document.getElementById("error_" + key);

			error = types[type](key);
			if (error === true) {
				ok = false;
				// Error already shown elsewhere.
				msg.style.display = "none";
			} else if (error) {
				ok = false;
				msg.innerText = error;
				msg.style.display = "block";
			} else {
				msg.style.display = "none";
			}
		}
	}

	return ok;
}

function validateAndSend(event) {
	if (validate()) {
		var form = document.getElementById("page");
		form.submit();
	}
}

function updateHint(element) {
	var name = element.name;
	var hints = document.getElementsByName(name + "_hint");
	if (hints.length > 0) {
		var hint = hints[0];
		var enabled = true;
		if (element.value == "") {
			hint.innerText = document.errors.no_value || "Select a type";
		} else {
			var info = document.value_types[element.value];
			hint.innerText = info.hint || "";
			enabled = info.format.includes("{}");
		}

		var input = document.getElementsByName(name + "_val");
		if (input.length > 0) {
			input[0].disabled = !enabled;
		}
	}
}

function updateHints() {
	for (var i = 0; ; i++) {
		var type = findElem("type_" + i);
		var key = findElem("key_" + i);
		if (!type || !key)
			break;

		type = type.value;
		key = key.value;

		if (type === "value") {
			updateHint(findElem(key));
		}
	}
}
