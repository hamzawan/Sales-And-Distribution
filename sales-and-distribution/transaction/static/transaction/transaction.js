$(document).ready(function () {

	// var $loading = $('#loading').hide();

	var arr = [];
	var count = 1;
	var sum = 0;
	var edit_id;
	var price = 0;
	var quantity;
	var amount;
	var total = 0
	var grand = 0;


	$(".has_id").click(function () {
		edit_id = this.id;
	});

	$('#credit_days').prop('disabled', 'disabled');
	$('#payment_method').change(function () {
		if ($(this).val() == "Credit") {
			$('#credit_days').removeAttr('disabled');
		} else {
			$('#credit_days').prop('disabled', 'disabled');
		}
	});

	function getCookie(c_name) {
		if (document.cookie.length > 0) {
			c_start = document.cookie.indexOf(c_name + "=");
			if (c_start != -1) {
				c_start = c_start + c_name.length + 1;
				c_end = document.cookie.indexOf(";", c_start);
				if (c_end == -1) c_end = document.cookie.length;
				return unescape(document.cookie.substring(c_start, c_end));
			}
		}
		return "";
	}

	$('#x_stand_purchase').keypress(function (e) {
		e.preventDefault();
		if (e.which == 13) {
			var x_stand = $('#x_stand_purchase').val();

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase/new/',
					data: {
						'x_stand': x_stand,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><pre>' + type[0].fields["item_description"] + '</pre></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0</td>' +
						'<td id="height">0</td>' +
						'<td id="quantity"><input type="text" required style="width:80px;" class="form-control input_x_quantity"></td>' +
						'<td id="sqft">0</td>' +
						'<td id="rate"><input type="text" required style="width:80px;" class="form-control input_x_rate"></td>' +
						'<td id="total" style="font-weight:bold;" required class="sum"><b>0.00</b></td>' +
						'<td style="display:none;" id="measurment">pieces</td>' +
						'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_purchase').val("");

				});
		}
	})

	$(".add-item-x-purchase").click(function () {
		var x_stand = $('#x_stand_purchase').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/purchase/new/',
				data: {
					'x_stand': x_stand,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><pre>' + type[0].fields["item_description"] + '</pre></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0</td>' +
					'<td id="height">0</td>' +
					'<td id="quantity"><input type="text" required style="width:80px;" class="form-control input_x_quantity"></td>' +
					'<td id="sqft">0</td>' +
					'<td id="rate"><input type="text" required style="width:80px;" class="form-control input_x_rate"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;" id="measurment">pieces</td>' +
					'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
				$('[data-toggle="tooltip"]').tooltip();
				$('#item_code_purchase').val("");

			});
	});


	$("#new-purchase-table").on('keyup', '.input_x_quantity', function () {
		var input_x_quantity = $(this).val();
		var input_x_rate = $(this).parents('tr').find('input.input_x_rate').val();
		if (isNaN(input_x_rate) && input_x_rate) {
			input_x_rate = 0
		}
		var total = input_x_quantity * input_x_rate;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
		$(this).parents('tr').find('#measurment').text("pieces");
	});

	// PURCHASE DISCOUNT FOR NEW PURCHASE

	$("#new_purchase_dicsount_in_val").on('keyup', function () {
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		if (v) {
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#new_purchase_discount").val(discount_in_percentage);
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		} else {
			v = 0
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = 0
			$("#new_purchase_discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		}
	})


	$("#new_purchase_discount").on('keyup', function () {
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		if (v) {
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_amount_in_per = discount_amount * amount_before_discount / 100
			$("#new_purchase_dicsount_in_val").val(discount_amount_in_per);
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount_in_per);
			}
		} else {
			v = 0
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#purchase_discount").val(0);
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		}
	})

	// END NEW PURCHASE DISCOUNT

	// PURCHASE DISCOUNT FOR EDIT

	$("#purchase_dicsount_in_val").on('keyup', function () {
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		if (v) {
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#purchase_discount").val(discount_in_percentage);
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		} else {
			v = 0
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#purchase_discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		}
	})


	$("#purchase_discount").on('keyup', function () {
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		if (v) {
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_amount_in_per = discount_amount * amount_before_discount / 100
			$("#purchase_dicsount_in_val").val(discount_amount_in_per.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount_in_per);
			}
		} else {
			v = 0
			var amount_before_discount = parseFloat(sum);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#purchase_discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) - discount_amount);
			}
		}
	})


	// END PURCHASE EDIT DISCOUNT

	$("#new-purchase-table").on('keyup', '.input_x_rate', function () {
		var input_x_rate = $(this).val();
		var input_x_quantity = $(this).parents('tr').find('input.input_x_quantity').val();
		if (isNaN(input_x_quantity) && input_x_quantity) {
			input_x_quantity = 0
		}
		var total = input_x_quantity * input_x_rate;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		var sum = 0;
		discount_in_val = $("#new_purchase_dicsount_in_val").val()
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			$('#grand_total').val(sum.toFixed(2) - discount_in_val);
		});
		$(this).parents('tr').find('#measurment').text("pieces");
	});

	$('#new-purchase-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(11)'); //locate the <td> holding select;
		var total = tdObject.text() //grab the <select> tag assuming that there will be only single select box within that <td>
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}
		$('#grand_total').val(sum.toFixed(2));
	});

	$("#item_code_purchase").keypress(function (e) {
		e.preventDefault();
		if (e.which == 13) {
			var item_code_purchase = $('#item_code_purchase').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase/new/',
					data: {
						'item_code_purchase': item_code_purchase,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)

					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + type[0].fields['item_code'] + '</td>' +
						'<td>' + type[0].fields['item_name'] + '</td>' +
						'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
						'<td ><select id="sel" class="form-control input_select" style="height:40px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
						'<td id="width"><input type="text" required class="form-control input_width"></td>' +
						'<td id="height"><input type="text" required class="form-control input_height"></td>' +
						'<td id="quantity"><input type="text" required class="form-control input_quantity"></td>' +
						'<td id="square_fit"></td>' +
						'<td id="rate" ><input type="text" style="width:70px;" required class="form-control input_rate"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;" id="measurment">sq.ft</td>' +
						'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");
				});
		}
	})

	$(".add-item-purchase").click(function () {
		var item_code_purchase = $('#item_code_purchase').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/purchase/new/',
				data: {
					'item_code_purchase': item_code_purchase,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields['item_code'] + '</td>' +
					'<td>' + type[0].fields['item_name'] + '</td>' +
					'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
					'<td ><select id="sel" class="form-control input_select" style="height:40px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
					'<td id="width"><input type="text" required class="form-control input_width"></td>' +
					'<td id="height"><input type="text" required class="form-control input_height"></td>' +
					'<td id="quantity"><input type="text" required class="form-control input_quantity"></td>' +
					'<td id="square_fit"></td>' +
					'<td id="rate" ><input type="text" style="width:70px;" required class="form-control input_rate"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;" id="measurment">sq.ft</td>' +
					'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
				$('[data-toggle="tooltip"]').tooltip();
				$('#item_code_sale').val("");
			});
	});

	$("#new-purchase-table").on('keyup', '.input_width', function () {
		var input_width = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_height = $(this).parents('tr').find('input.input_height').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}
		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	});


	$("#purchase-return-table").on('keyup', '.input_width', function () {
		var input_width = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_height = $(this).parents('tr').find('input.input_height').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}
		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#discount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})


	$("#new-purchase-table").on('keyup', '.input_height', function () {
		var input_height = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_width = $(this).parents('tr').find('input.input_width').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = parseFloat(input_width) * parseFloat(input_height);
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {

			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})


	$("#purchase-return-table").on('keyup', '.input_height', function () {
		var input_height = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_width = $(this).parents('tr').find('input.input_width').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = parseFloat(input_width) * parseFloat(input_height);
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {

			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#discount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})


	$("#new-purchase-table").on('keyup', '.input_quantity', function () {
		var input_quantity = $(this).val();
		var input_height = $(this).parents('tr').find('input.input_height').val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}
		var input_width = $(this).parents('tr').find('input.input_width').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				console.log(total);

				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#new-purchase-table").on('keyup', '.input_rate', function () {
		var input_rate = $(this).val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_width = $(this).parents('tr').find('input.input_width').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_height = $(this).parents('tr').find('input.input_height').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}

		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				console.log(total);

				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#purchase-return-table").on('keyup', '.input_rate', function () {
		var input_rate = $(this).val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		var input_select = $(this).parents('tr').find('select.input_select').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_width = $(this).parents('tr').find('input.input_width').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_height = $(this).parents('tr').find('input.input_height').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}

		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				console.log(total);

				sum += parseFloat(total);
			}
			discount_amount = $("#discount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#new-purchase-table").on('change', '.input_select', function () {
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_width = $(this).parents('tr').find('input.input_width').val();
		var input_height = $(this).parents('tr').find('input.input_height').val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		var input_rate = $(this).parents('tr').find('input.input_rate').val();

		if (isNaN(input_width) && input_width) {
			input_width = 0
		}

		if (isNaN(input_height) && input_height) {
			input_height = 0
		}

		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#new_purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	});


	$("#purchase-return-table").on('change', '.input_select', function () {
		var input_select = $(this).parents('tr').find('select.input_select').val();
		var input_width = $(this).parents('tr').find('input.input_width').val();
		var input_height = $(this).parents('tr').find('input.input_height').val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity').val();
		var input_rate = $(this).parents('tr').find('input.input_rate').val();

		if (isNaN(input_width) && input_width) {
			input_width = 0
		}

		if (isNaN(input_height) && input_height) {
			input_height = 0
		}

		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#discount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	});

	// 	$(document).on("click", ".add-transaction-purchase", function(){
	// 		$(this).parents("tr").find('select').prop('disabled', 'disabled');
	// 		sum = 0;
	// 			var empty = false;
	// 			var input = $(this).parents("tr").find('input[type="text"]');
	// 					input.each(function(){
	// 				if(!$(this).val()){
	// 					$(this).addClass("error");
	// 					empty = true;
	// 				}
	// 				else{
	// 						$(this).removeClass("error");
	// 						}

	// 			});

	// 		$(this).parents("tr").find(".error").first().focus();
	// 		if(!empty){
	// 			input.each(function(){
	// 				$(this).parent("td").html($(this).val());
	// 			});
	// 			$(this).parents("tr").find(".add-transaction-purchase, .edit-transaction-purchase").toggle();
	// 			$(".add-item-purchase").removeAttr("disabled");
	// 		}

	// 		var meas = $(this).parents("tr").find('select').val()
	// 		$('#new-purchase-table tbody tr').each(function() {
	// 				var tdObject = $(this).find('td:eq(4)');
	// 				var selectObject = tdObject.find("select");
	// 	});

	// var get_height = $($(this).parents("tr").find("#height")).filter(function() {
	// 				height = $(this).text();
	// 				return height
	// 		}).closest("tr");

	// var get_width = $($(this).parents("tr").find("#width")).filter(function() {
	// 				width = $(this).text();
	// 				return width
	// 		}).closest("tr");


	// var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
	// 				quantity = $(this).text();
	// 				return quantity
	// 		}).closest("tr");
	// 		console.log("HERE IS MEAS",meas);
	// if (meas === "sq.ft") {
	// 	square_fit = parseFloat(width) * parseFloat(height);
	// 	square_fit = square_fit * parseFloat(quantity)
	// 	var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 					$(this).text(square_fit.toFixed(2));
	// 					return square_fit
	// 			}).closest("tr");
	// 	var get_meas = $($(this).parents("tr").find("#measurment")).filter(function() {
	// 					meas = $(this).text("sq.ft");
	// 					return meas
	// 			}).closest("tr");
	// }
	// else if (meas === "sq.inches") {
	// 	square_fit = parseFloat(width) * parseFloat(height)
	// 	square_fit = square_fit / 144
	// 	square_fit = square_fit * parseFloat(quantity)
	// 	var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 					$(this).text(square_fit.toFixed(2));
	// 					return square_fit
	// 			}).closest("tr");
	// 	var get_meas = $($(this).parents("tr").find("#measurment")).filter(function() {
	// 					meas = $(this).text("sq.inches");
	// 					return meas
	// 			}).closest("tr");
	// }

	//   var get_sqft = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 				sqft = $(this).text();
	// 				return sqft;
	// 		}).closest("tr");

	// 	var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 					rate = $(this).text();
	// 					return rate;
	// 			}).closest("tr");


	// 	total = parseFloat(sqft) * parseFloat(rate)

	// 	var check_condition = $($(this).parents("tr").find("#width")).filter(function() {
	// 		check = $(this).text();
	// 		return check;
	// }).closest("tr");
	// 	if (check == "0") {
	// 		var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
	// 					quantity = $(this).text();
	// 					return quantity;
	// 			}).closest("tr");

	// 		var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 					rate = $(this).text();
	// 					return rate;
	// 			}).closest("tr");

	// 		var total = parseFloat(quantity) * parseFloat(rate)
	// 		var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 					$(this).text(total.toFixed(2));
	// 					return total;
	// 			}).closest("tr");
	// 	}
	// 	else {
	// 		var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 					total = $(this).text(total.toFixed(2));
	// 					console.log(this);
	// 					return total;
	// 			}).closest("tr");
	// 	}
	// 	});

	// // Edit row on edit button click
	// $(document).on("click", ".edit-transaction-purchase", function(){
	// 	$(this).parents("tr").find('select').prop('disabled', false);
	// 		$(this).parents("tr").find("td:not(:last-child)").each(function(i){
	// 			if (i === 5) {
	// 				 if ($(this).text() == "0") {
	// 				 }
	// 				 else {
	// 					$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				 }

	// 			}
	// 			if (i === 6) {
	// 				 if ($(this).text() == "0") {
	// 				 }
	// 				 else {
	// 					$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				 }

	// 			}
	// 			if (i === 7) {
	// 				 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 			}
	// 			if (i === 9) {
	// 				 $(this).html('<input type="text" style="width:80px;" class="form-control" value="' + $(this).text() + '">');
	// 			  }
	// 	});
	// 	$(this).parents("tr").find(".add-transaction-purchase, .edit-transaction-purchase").toggle();
	// 	$(".add-item-purchase").attr("disabled", "disabled");
	// 	});

	// Delete row on delete button click
	$(document).on("click", ".delete-transaction-purchase", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-purchase").removeAttr("disabled");
		after_delete_purchase();
	});


	function after_delete_purchase() {
		var delete_sum = 0;
		$('#new-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				delete_sum += parseFloat(total);
			}
			$('#grand_total').val(delete_sum.toFixed(2));
		});
	}



	$('#new-purchase-submit').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#new-purchase-table');
		var data = [];
		var purchase_id = $('#purchase_id').val();
		var follow_up = $('#follow_up').val();
		var vendor = $('#vendor').val();
		var purchase_discount = $('#new_purchase_discount').val();
		var new_purchase_dicsount_in_val = $('#new_purchase_dicsount_in_val').val();
		var payment_method = $('#payment_method').val();
		var footer_desc = $('#footer_desc').val();


		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'width': "",
					'height': "",
					'quantity': "",
					'sqft': "",
					'rate': "",
					'total': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					var is_und;
					if (i === 1) {
						row["item_code"] = ($(this).text());
					} else if (i === 5) {
						is_und = ($(this).find('input').val());
						if (typeof is_und == 'undefined') {
							row["width"] = "0";
						} else {
							row["width"] = ($(this).find('input').val());
						}
					} else if (i === 6) {
						is_und = ($(this).find('input').val());
						if (typeof is_und == 'undefined') {
							row["height"] = "0";
						} else {
							row["height"] = ($(this).find('input').val());
						}
					} else if (i === 7) {
						row["quantity"] = ($(this).find('input').val());
					} else if (i === 8) {
						row["sqft"] = ($(this).text());
					} else if (i === 9) {
						row["rate"] = ($(this).find('input').val());
					} else if (i === 10) {
						row["total"] = ($(this).text());
					} else if (i === 11) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});
		req = $.ajax({
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			},
			type: 'POST',
			url: '/transaction/purchase/new/',
			data: {
				'purchase_id': purchase_id,
				'vendor': vendor,
				'follow_up': follow_up,
				'payment_method': payment_method,
				'footer_desc': footer_desc,
				'purchase_discount': purchase_discount,
				'new_purchase_dicsount_in_val': new_purchase_dicsount_in_val,
				'items': JSON.stringify(data),
			},
			dataType: 'json'
		})
		req.done(function done(data) {
			if (data.result) {
				$.toast().reset('all');
				$.toast({
					heading: 'Submitted Successfully',
					text: 'Yes! check here <a href="/transaction/purchase/print/' + data.header_id + '" target="_blank">' + data.purchase_id + '</a>.',
					hideAfter: false,
					icon: 'success',
					'position': 'mid-center'
				})
				setInterval(function () {
					location.reload()
				}, 2000);
			} else {
				$(".disable_on_submit").prop('disabled', false);
				var myToast = $.toast({
					text: data.e,
					hideAfter: false,
					bgColor: '#E01A31',
					'position': 'bottom-left',
					icon: 'error'
				});
			}

		})
	});

	// =================================================================================
	sum = 0
	discount_amount = 0
	$('#edit-purchase-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(11)'); //locate the <td> holding select;
		var total = tdObject.text() //grab the <select> tag assuming that there will be only single select box within that <td>
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}
		discount_amount_in_per = $("#purchase_discount").val();
		discount_amount = sum * discount_amount_in_per / 100
		$("#purchase_dicsount_in_val").val(discount_amount.toFixed(2))

	});
	$('#grand_total').val((sum - discount_amount).toFixed(2));
	$('#item_code_purchase_edit').keypress(function (e) {
		e.preventDefault();
		edit_id = $(this).attr("data-id")
		if (e.which == 13) {
			var item_code_purchase = $('#item_code_purchase_edit').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: `/transaction/purchase/edit/${edit_id}`,
					data: {
						'item_code_purchase': item_code_purchase,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					var type = JSON.parse(data.items);
					var index = $("table tbody tr:last-child").index();
					total_amount = (type[0].fields['unit_price'] * type[0].fields['quantity']);
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td style="display:none;">' + type[0]['pk'] + '</td>' +
						'<td>' + type[0].fields['item_code'] + '</td>' +
						'<td>' + type[0].fields['item_name'] + '</td>' +
						'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
						'<td ><select id="sel" class="form-control form-control-sm input_select_edit" style="height:40px;width:80px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
						'<td id="width"><input type="text"  style="width:60px;" class="form-control input_width_edit"></td>' +
						'<td id="height"><input type="text" style="width:60px;" class="form-control input_height_edit"></td>' +
						'<td id="quantity"><input type="text" style="width:60px;" class="form-control input_quantity_edit"></td>' +
						'<td id="square_fit"></td>' +
						'<td id="rate" ><input type="text" style="width:70px;" class="form-control input_rate_edit"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;" id="measurment">sq.ft</td>' +
						'<td><a class="delete-purchase-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
				});
		}
	});

	$(".add-item-purchase-edit").click(function () {
		var item_code_purchase = $('#item_code_purchase_edit').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/purchase/edit/${edit_id}`,
				data: {
					'item_code_purchase': item_code_purchase,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var type = JSON.parse(data.items);
				var index = $("table tbody tr:last-child").index();
				total_amount = (type[0].fields['unit_price'] * type[0].fields['quantity']);
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td style="display:none;">' + type[0]['pk'] + '</td>' +
					'<td>' + type[0].fields['item_code'] + '</td>' +
					'<td>' + type[0].fields['item_name'] + '</td>' +
					'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
					'<td ><select id="sel" class="form-control form-control-sm input_select_edit" style="height:40px;width:80px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
					'<td id="width"><input type="text"  style="width:60px;" class="form-control input_width_edit"></td>' +
					'<td id="height"><input type="text" style="width:60px;" class="form-control input_height_edit"></td>' +
					'<td id="quantity"><input type="text" style="width:60px;" class="form-control input_quantity_edit"></td>' +
					'<td id="square_fit"></td>' +
					'<td id="rate" ><input type="text" style="width:70px;" class="form-control input_rate_edit"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;" id="measurment">sq.ft</td>' +
					'<td><a class="delete-purchase-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
			});
	})
	$('#x_stand_edit').keypress(function (e) {
		e.preventDefault()
		edit_id = $(this).attr("data-id")
		if (e.which == 13) {
			var job_no_sale = "";
			var x_stand_edit = $('#x_stand_edit').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: `/transaction/purchase/edit/${edit_id}`,
					data: {
						'x_stand_edit': x_stand_edit,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td style="display:none;">' + type[0]['pk'] + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><pre>' + type[0].fields["item_description"] + '</pre></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0.00</td>' +
						'<td id="height">0.00</td>' +
						'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_edit"></td>' +
						'<td id="sqft">0.00</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_edit"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;">pieces</td>' +
						'<td><a class="delete-purchase-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-purchase-edit, .add-purchase-edit").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");

				});
		}
	});

	$(".add-item-x-edit-purchase").click(function () {

		var job_no_sale = "";
		var x_stand_edit = $('#x_stand_edit').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/purchase/edit/${edit_id}`,
				data: {
					'x_stand_edit': x_stand_edit,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td style="display:none;">' + type[0]['pk'] + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><pre>' + type[0].fields["item_description"] + '</pre></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0.00</td>' +
					'<td id="height">0.00</td>' +
					'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_edit"></td>' +
					'<td id="sqft">0.00</td>' +
					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_edit"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;">pieces</td>' +
					'<td><a class="delete-purchase-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$('#item_code_sale').val("");
			});
	});

	$("#edit-purchase-table").on('keyup', '.input_width_edit', function () {
		var input_width = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select_edit').val();
		var input_height = $(this).parents('tr').find('input.input_height_edit').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity_edit').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate_edit').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}
		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#edit-purchase-table").on('keyup', '.input_height_edit', function () {

		var input_height = $(this).val();
		var input_select = $(this).parents('tr').find('select.input_select_edit').val();
		var input_width = $(this).parents('tr').find('input.input_width_edit').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_quantity = $(this).parents('tr').find('input.input_quantity_edit').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate_edit').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = parseFloat(input_width) * parseFloat(input_height);
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			discount_amount = $("#purchase_dicsount_in_val").val();

			$('#grand_total').val(sum.toFixed(2));

		});
	})


	$("#edit-purchase-table").on('keyup', '.input_quantity_edit', function () {
		var input_quantity = $(this).val();
		var input_height = $(this).parents('tr').find('input.input_height_edit').val();
		var input_select = $(this).parents('tr').find('select.input_select_edit').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}
		var input_width = $(this).parents('tr').find('input.input_width_edit').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_rate = $(this).parents('tr').find('input.input_rate_edit').val();
		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#edit-purchase-table").on('keyup', '.input_rate_edit', function () {
		var input_rate = $(this).val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity_edit').val();
		var input_select = $(this).parents('tr').find('select.input_select_edit').val();
		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}
		var input_width = $(this).parents('tr').find('input.input_width_edit').val();
		if (isNaN(input_width) && input_width) {
			input_width = 0
		}
		var input_height = $(this).parents('tr').find('input.input_height_edit').val();
		if (isNaN(input_height) && input_height) {
			input_height = 0
		}

		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2));
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}

		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#purchase_dicsount_in_val").val()
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	})

	$("#edit-purchase-table").on('change', '.input_select_edit', function () {
		var input_select = $(this).parents('tr').find('select.input_select_edit').val();
		var input_width = $(this).parents('tr').find('input.input_width_edit').val();
		var input_height = $(this).parents('tr').find('input.input_height_edit').val();
		var input_quantity = $(this).parents('tr').find('input.input_quantity_edit').val();
		var input_rate = $(this).parents('tr').find('input.input_rate_edit').val();

		if (isNaN(input_width) && input_width) {
			input_width = 0
		}

		if (isNaN(input_height) && input_height) {
			input_height = 0
		}

		if (isNaN(input_rate) && input_rate) {
			input_rate = 0
		}

		if (isNaN(input_quantity) && input_quantity) {
			input_quantity = 0
		}


		if (input_select == "sq.ft") {
			square_fit = input_width * input_height;
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.ft");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		} else if (input_select = "sq.inches") {
			square_fit = input_width * input_height;
			square_fit = square_fit / 144
			total_square_fit = input_quantity * square_fit
			total = total_square_fit * input_rate
			var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
			$(this).parents('tr').find('#measurment').text("sq.inches");
			$(this).parents('tr').find('#square_fit').text(total_square_fit.toFixed(2))
		}
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			discount_amount = $("#purchase_dicsount_in_val").val();
			$('#grand_total').val(sum.toFixed(2) - discount_amount);
		});
	});


	$("#edit-purchase-table").on('keyup', '.input_x_quantity_edit', function () {
		var input_x_quantity = $(this).val();
		var input_x_rate = $(this).parents('tr').find('input.input_x_rate_edit').val();
		if (isNaN(input_x_rate) && input_x_rate) {
			input_x_rate = 0
		}
		var total = input_x_quantity * input_x_rate;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			$('#grand_total').val(sum.toFixed(2));
		});
		$(this).parents('tr').find('#measurment').text("pieces");
	});


	$("#edit-purchase-table").on('keyup', '.input_x_rate_edit', function () {
		var input_x_rate = $(this).val();
		var input_x_quantity = $(this).parents('tr').find('input.input_x_quantity_edit').val();
		if (isNaN(input_x_quantity) && input_x_quantity) {
			input_x_quantity = 0
		}
		var total = input_x_quantity * input_x_rate;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		var sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			$('#grand_total').val(sum.toFixed(2));
		});
		$(this).parents('tr').find('#measurment').text("pieces");
	});

	$('#new-purchase-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(11)'); //locate the <td> holding select;
		var total = tdObject.text() //grab the <select> tag assuming that there will be only single select box within that <td>
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}
		$('#grand_total').val(sum.toFixed(2));
	});
	// Add row on add button click
	// 	$(document).on("click", ".add-purchase-edit", function(){
	// 		$('#sel').prop('disabled', 'disabled');
	// 		sum = 0;
	// 			var empty = false;
	// 			var input = $(this).parents("tr").find('input[type="text"]');
	// 					input.each(function(){
	// 				if(!$(this).val()){
	// 					$(this).addClass("error");
	// 					empty = true;
	// 				}
	// 				else{
	// 						$(this).removeClass("error");
	// 						}

	// 			});

	// 		$(this).parents("tr").find(".error").first().focus();
	// 		if(!empty){
	// 			input.each(function(){
	// 				$(this).parent("td").html($(this).val());
	// 			});
	// 			$(this).parents("tr").find(".add-purchase-edit, .edit-purchase-edit").toggle();
	// 			$(".add-item-purchase-edit").removeAttr("disabled");
	// 		}

	// 	 var check_condition = $($(this).parents("tr").find("#width")).filter(function() {
	// 				 check = $(this).text();
	// 				 return check;
	// 		 }).closest("tr");
	// 		 console.log(check);
	// 	 if (check == "0.00") {
	// 		 console.log("Hamza");
	// 		 var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
	// 					 quantity = $(this).text();
	// 					 return quantity;
	// 			 }).closest("tr");

	// 		 var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 					 rate = $(this).text();
	// 					 return rate;
	// 			 }).closest("tr");

	// 		 var total = parseFloat(quantity) * parseFloat(rate)
	// 		 console.log(total);
	// 		 var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 					 $(this).text(total.toFixed(2));
	// 					 return total;
	// 			 }).closest("tr");
	// 	 }
	// 	 else {
	// 		 var meas;
	// 				 $('#edit-purchase-table tbody tr').each(function() {
	// 						 var tdObject = $(this).find('td:eq(5)'); //locate the <td> holding select;
	// 						 var selectObject = tdObject.find("select"); //grab the <select> tag assuming that there will be only single select box within that <td>
	// 						 meas = selectObject.val(); // get the selected country from current <tr>
	// 			 });

	// 		 var get_height = $($(this).parents("tr").find("#height")).filter(function() {
	// 						 height = $(this).text();
	// 						 return height
	// 				 }).closest("tr");

	// 		 var get_width = $($(this).parents("tr").find("#width")).filter(function() {
	// 						 width = $(this).text();
	// 						 return width
	// 				 }).closest("tr");


	// 		 var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
	// 						 quantity = $(this).text();
	// 						 return quantity
	// 				 }).closest("tr");
	// 		 if (meas === "sq.ft") {
	// 			 square_fit = parseFloat(width) * parseFloat(height);
	// 			 square_fit = square_fit * parseFloat(quantity)
	// 			 var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 							 $(this).text(square_fit.toFixed(2));
	// 							 return square_fit
	// 					 }).closest("tr");
	// 			 var get_meas = $($(this).parents("tr").find("#measurment")).filter(function() {
	// 							 meas = $(this).text("sq.ft");
	// 							 return meas
	// 					 }).closest("tr");
	// 		 }
	// 		 else if (meas === "sq.inches") {
	// 			 square_fit = parseFloat(width) * parseFloat(height)
	// 			 square_fit = square_fit / 144
	// 			 square_fit = square_fit * parseFloat(quantity)
	// 			 var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 							 $(this).text(square_fit.toFixed(2));
	// 							 return square_fit
	// 					 }).closest("tr");
	// 			 var get_meas = $($(this).parents("tr").find("#measurment")).filter(function() {
	// 							 meas = $(this).text("sq.inches");
	// 							 return meas
	// 					 }).closest("tr");
	// 		 }

	// 			 var get_sqft = $($(this).parents("tr").find("#square_fit")).filter(function() {
	// 						 sqft = $(this).text();
	// 						 return sqft;
	// 				 }).closest("tr");

	// 			 var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 							 rate = $(this).text();
	// 							 return rate;
	// 					 }).closest("tr");


	// 			 total = parseFloat(sqft) * parseFloat(rate)

	// 			 var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 							 total = $(this).text(total.toFixed(2));
	// 							 return total;
	// 					 }).closest("tr");

	// 			//the value of sum needs to be reset for each row, so it has to be set inside the row loop
	// 			var sum = 0
	// 			//find the combat elements in the current row and sum it
	// 			$(this).find('.sum').each(function () {
	// 					var total = $(this).text();
	// 					if (!isNaN(total) && total.length !== 0) {
	// 							sum += parseFloat(total);
	// 					}
	// 						});
	// 						//set the value of currents rows sum to the total-combat element in the current row

	// 	 }

	// 	 $('#edit-purchase-table tbody tr').each(function() {
	// 			 var tdObject = $(this).find('td:eq(11)'); //locate the <td> holding select;
	// 			 var total = tdObject.text() //grab the <select> tag assuming that there will be only single select box within that <td>
	// 			 console.log($(this).find('td:eq(11)'));
	// 			 if (!isNaN(total) && total.length !== 0) {
	// 					 sum += parseFloat(total);
	// 			 }
	// 			 $('#grand_total').val(sum.toFixed(2));
	//  });

	// 	});


	// Edit row on edit button click
	// $(document).on("click", ".edit-purchase-edit", function(){
	// 		$('#sel').prop('disabled', false);
	// 		$(this).parents("tr").find("td:not(:last-child)").each(function(i){
	// 				if (i === 6) {
	// 					$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				}
	// 				if (i === 7) {
	// 					$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				}
	// 				if (i === 8) {
	// 					 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				}
	// 				if (i === 10) {
	// 					 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 				}

	// 			});
	// 			$(this).parents("tr").find(".add-purchase-edit, .edit-purchase-edit").toggle();
	// 			$(".add-item-purchase-edit").attr("disabled", "disabled");
	// 			});

	// Delete row on delete button click
	$(document).on("click", ".delete-purchase-edit", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-purchase-edit").removeAttr("disabled");

		after_delete_purchase_edit();
	});


	function after_delete_purchase_edit() {
		var delete_sum = 0;
		$('#edit-purchase-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				delete_sum += parseFloat(total);
			}
			$('#grand_total').val(delete_sum.toFixed(2));
		});
	}

	//EDIT PURCHASE END

	$('#edit-purchase-submit').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#edit-purchase-table');
		var data = [];
		var purchase_id = $('#purchase_id').val();
		var supplier = $('#supplier_name_purchase').val();
		var payment_method = $('#payment_method').val();
		var follow_up = $('#follow_up').val();
		var purchase_discount = $('#purchase_discount').val();
		var purchase_dicsount_in_val = $('#purchase_dicsount_in_val').val();
		var footer_desc = $('#footer_desc').val();


		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'id': "",
					'width': "",
					'height': "",
					'quantity': "",
					'sqft': "",
					'rate': "",
					'total': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					var is_und;
					if (i === 1) {
						row["id"] = ($(this).text());
					} else if (i === 6) {
						is_und = ($(this).find('input').val());
						if (typeof is_und == 'undefined') {
							row["width"] = "0";
						} else {
							row["width"] = ($(this).find('input').val());
						}
					} else if (i === 7) {
						is_und = ($(this).find('input').val());
						if (typeof is_und == 'undefined') {
							row["height"] = "0";
						} else {
							row["height"] = ($(this).find('input').val());
						}
					} else if (i === 8) {
						row["quantity"] = ($(this).find('input').val());
					} else if (i === 9) {
						row["sqft"] = ($(this).text());
					} else if (i === 10) {
						row["rate"] = ($(this).find('input').val());

					} else if (i === 11) {
						row["total"] = ($(this).text());
					} else if (i === 12) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});



		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/purchase/edit/${edit_id}`,
				data: {
					'purchase_id': purchase_id,
					'supplier': supplier,
					'payment_method': payment_method,
					'follow_up': follow_up,
					'purchase_discount': purchase_discount,
					'purchase_dicsount_in_val': purchase_dicsount_in_val,
					'footer_desc': footer_desc,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (data.result) {
					$.toast().reset('all');
					$.toast({
						heading: 'Updated Successfully',
						text: 'Yes! check here <a href="/transaction/purchase/print/' + data.header_id + '" target="_blank">' + data.purchase_id + '</a>.',
						hideAfter: false,
						icon: 'success',
						'position': 'mid-center'
					})
					setInterval(function () {
						location.reload()
					}, 2000);
				} else {
					$(".disable_on_submit").prop('disabled', false);
					var myToast = $.toast({
						text: data.e,
						hideAfter: false,
						bgColor: '#E01A31',
						'position': 'bottom-left',
						icon: 'error'
					});
				}
			})
	});

	// =============================================================================


	$('#edit-purchase-return-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-purchase-return-table');
		var data = [];
		var purchase_id = $('#purchase_return_id').val();
		var supplier = $('#supplier_purchase_return_name').val();
		var payment_method = $('#payment_method').val();
		var footer_desc = $('#desc_purchase_return').val();


		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'item_name': "",
					'item_description': "",
					'quantity': "",
					'unit': "",
					'price': "",
					'sales_tax': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 2) {
						row["item_name"] = ($(this).text());
					} else if (i === 3) {
						row["item_description"] = ($(this).text());
					} else if (i === 4) {
						row["quantity"] = ($(this).text());
					} else if (i === 5) {
						row["unit"] = ($(this).text());
					} else if (i === 6) {
						row["price"] = ($(this).text());
					} else if (i === 7) {
						row["sales_tax"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/purchase/return/edit/${edit_id}`,
				data: {
					'purchase_id': purchase_id,
					'supplier': supplier,
					'payment_method': payment_method,
					'footer_desc': footer_desc,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done() {
				alert("Purchase Return Updated");
				location.reload();
			})
	});


	// =============================================================================
	$('#new-sale-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(10)');
		var total = tdObject.text()
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}
		$('#grand_total').val(sum.toFixed(2));
	});

	$(".add-item-sale").click(function () {
		var job_no_sale = "";
		var job_no_sale = $('#job_no_sale').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/sale/new/',
				data: {
					'job_no_sale': job_no_sale,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				for (var i = 0; i < data.items.length; i++) {
					if (data.items[i][3] == "sq.ft") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit * parseFloat(data.items[i][6])
					} else if (data.items[i][3] == "sq.inches") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit / 144
						square_fit = square_fit * parseFloat(data.items[i][6])
					}
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + data.items[i][0] + '</td>' +
						'<td>' + data.items[i][1] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control"></td>' +
						'<td>' + data.items[i][3] + '</td>' +
						'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
						'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
						'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
						'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;">' + data.items[i][3] + '</td>' +
						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$('#item_code_sale').val("");
				}
			});
	});


	$('#job_no_sale').on('keypress', function (e) {
		if (e.which == 13) {
			e.preventDefault();
			var job_no_sale = "";
			var job_no_sale = $('#job_no_sale').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale/new/',
					data: {
						'job_no_sale': job_no_sale,
					},
					dataType: 'json'
				})
				.done(function done(data) {

					for (var i = 0; i < data.items.length; i++) {
						if (data.items[i][3] == "sq.ft") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit * parseFloat(data.items[i][6])
						} else if (data.items[i][3] == "sq.inches") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit / 144
							square_fit = square_fit * parseFloat(data.items[i][6])
						}
						var index = $("table tbody tr:last-child").index();
						var row = '<tr>' +
							'<td>' + count + '</td>' +
							'<td>' + data.items[i][0] + '</td>' +
							'<td>' + data.items[i][1] + '</td>' +
							'<td><input type="text" style="width:300px;" class="form-control" value=" "></td>' +
							'<td>' + data.items[i][3] + '</td>' +
							'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
							'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
							'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
							'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
							'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
							'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
							'<td style="display:none;">' + data.items[i][3] + '</td>' +
							'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
							'</tr>';
						count++;
						$("table").append(row);
						$('#item_code_sale').val("");
					}
				});
		}
	});

	$(".add-item-x").click(function () {
		var x_stand = $('#x_stand').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/sale/new/',
				data: {
					'x_stand': x_stand,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><input type="text" style="width:300px;" class="form-control"></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0</td>' +
					'<td id="height">0</td>' +
					'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_sale"></td>' +
					'<td id="sqft">0</td>' +
					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_sale"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;"></td>' +
					'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$('#item_code_sale').val("");
			});
	});

	$('#x_stand').on('keypress', function (e) {
		if (e.which == 13) {
			e.preventDefault();
			var x_stand = $('#x_stand').val();

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale/new/',
					data: {
						'x_stand': x_stand,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control"></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0</td>' +
						'<td id="height">0</td>' +
						'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_sale"></td>' +
						'<td id="sqft">0</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_sale"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;"></td>' +
						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-sale, .add-transaction-sale").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");

				});
		}
	})

	$("#new-sale-table").on('keyup', '.input_rate_sale', function () {
		var input_rate_sale = $(this).val();
		var input_sq_ft = $(this).parents('tr').find('td#sqft').text();

		total = parseFloat(input_rate_sale) * parseFloat(input_sq_ft);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("sq.ft");

		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})

	$("#sale-return-table").on('keyup', '.input_rate_sale', function () {
		var input_rate_sale = $(this).val();
		var input_sq_ft = $(this).parents('tr').find('td#sqft').text();

		total = parseFloat(input_rate_sale) * parseFloat(input_sq_ft);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("sq.ft");

		var sum = 0;
		$('#sale-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})

	$("#purchase-return-table").on('keyup', '.input_rate_purchase', function () {
		var input_rate_sale = $(this).val();
		var input_sq_ft = $(this).parents('tr').find('td#sqft').text();

		total = parseFloat(input_rate_sale) * parseFloat(input_sq_ft);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("sq.ft");

		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})

	$("#new-sale-table").on('keyup', '.input_x_quantity_sale', function () {
		var input_x_quantity_sale = $(this).val();
		var input_rate_sale = $(this).parents('tr').find('input.input_x_rate_sale').val();
		if (isNaN(input_rate_sale) && input_rate_sale) {
			input_rate_sale = 0
		}
		total = input_rate_sale * parseFloat(input_x_quantity_sale);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#new-sale-table").on('keyup', '.input_x_rate_sale', function () {
		var input_x_rate_sale = $(this).val();
		var input_x_quantity_sale = $(this).parents('tr').find('input.input_x_quantity_sale').val();
		if (isNaN(input_x_quantity_sale) && input_x_quantity_sale) {
			input_x_quantity_sale = 0
		}
		total = input_x_rate_sale * input_x_quantity_sale;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#sale-return-table").on('keyup', '.input_x_quantity_sale', function () {
		var input_x_quantity_sale = $(this).val();
		var input_rate_sale = $(this).parents('tr').find('input.input_x_rate_sale').val();
		if (isNaN(input_rate_sale) && input_rate_sale) {
			input_rate_sale = 0
		}
		total = input_rate_sale * parseFloat(input_x_quantity_sale);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#sale-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#sale-return-table").on('keyup', '.input_x_rate_sale', function () {
		var input_x_rate_sale = $(this).val();
		var input_x_quantity_sale = $(this).parents('tr').find('input.input_x_quantity_sale').val();
		if (isNaN(input_x_quantity_sale) && input_x_quantity_sale) {
			input_x_quantity_sale = 0
		}
		total = input_x_rate_sale * input_x_quantity_sale;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#sale-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#purchase-return-table").on('keyup', '.input_x_quantity_purchase', function () {
		var input_x_quantity_purchase = $(this).val();
		var input_rate_sale = $(this).parents('tr').find('input.input_x_rate_purchase').val();
		if (isNaN(input_rate_sale) && input_rate_sale) {
			input_rate_sale = 0
		}
		total = input_rate_sale * parseFloat(input_x_quantity_purchase);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})




	$("#purchase-return-table").on('keyup', '.input_x_rate_purchase', function () {
		var input_x_rate_purchase = $(this).val();
		var input_x_quantity_purchase = $(this).parents('tr').find('input.input_x_quantity_purchase').val();
		if (isNaN(input_x_quantity_purchase) && input_x_quantity_purchase) {
			input_x_quantity_purchase = 0
		}
		total = input_x_rate_purchase * input_x_quantity_purchase;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})

	$("#new-sale-table").on('keyup', '.input_rate_sale', function () {
		var input_rate_sale = $(this).val();
		var input_sq_ft = $(this).parents('tr').find('td#sqft').text();

		total = parseFloat(input_rate_sale) * parseFloat(input_sq_ft);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("sq.ft");

		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}


			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})

	$("#srb").on('keyup', function () {
		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb_amount = (sum / 100) * v;
		var gst = $("#gst").val();
		var gst_amount = (sum / 100) * gst;
		var discount = $("#discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val").val();

		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		}

		var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)

		$("#discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val((parseFloat(sum) + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	});


	$("#gst").on('keyup', function () {
		var sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb = $("#srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst_amount = (sum / 100) * v;
		var discount = $("#discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val").val();
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		}

		var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})


	$("#discount_in_val").on('keyup', function () {
		var sum = 0;
		console.log("Hamza");
			
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		console.log(sum);
		
		var v = this.value;
		var srb = $("#srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst = $("#gst").val();
		var gst_amount = (sum / 100) * gst;
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		var discount_amount = parseFloat(v);
		var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#discount").val(discount_in_percentage.toFixed(2));
		console.log(discount_amount);
		
		if (!isNaN(v) && v.length != 0) {
			console.log(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})

	$("#discount_in_val_return").on('keyup', function () {
		var sum = 0;
		$('#sale-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb = $("#srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst = $("#gst").val();
		var gst_amount = (sum / 100) * gst;
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		var discount_amount = parseFloat(v);
		var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})


	$("#discount_in_val_return").on('keyup', function () {
		var sum = 0;
		$('#purchase-return-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(11)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb = $("#srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst = $("#gst").val();
		var gst_amount = (sum / 100) * gst;
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		var discount_amount = parseFloat(v);
		var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})

	// Add row on add button click
	$(document).on("click", ".add-transaction-sale", function () {
		sum = 0;
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}

		});

		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-transaction-sale, .edit-transaction-sale").toggle();
			$(".add-item-sale").removeAttr("disabled");
		}

		var get_sqft = $($(this).parents("tr").find("#sqft")).filter(function () {
			sqft = $(this).text();
			return sqft;
		}).closest("tr");

		var get_rate = $($(this).parents("tr").find("#rate")).filter(function () {
			rate = $(this).text();
			return rate;
		}).closest("tr");


		total = parseFloat(sqft) * parseFloat(rate)

		var check_condition = $($(this).parents("tr").find("#width")).filter(function () {
			check = $(this).text();
			return check;
		}).closest("tr");
		if (check == "0") {
			var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function () {
				quantity = $(this).text();
				return quantity;
			}).closest("tr");

			var get_rate = $($(this).parents("tr").find("#rate")).filter(function () {
				rate = $(this).text();
				return rate;
			}).closest("tr");

			var total = parseFloat(quantity) * parseFloat(rate)
			var get_total = $($(this).parents("tr").find("#total")).filter(function () {
				$(this).text(total.toFixed(2));
				return total;
			}).closest("tr");
		} else {
			var get_total = $($(this).parents("tr").find("#total")).filter(function () {
				total = $(this).text(total.toFixed(2));
				return total;
			}).closest("tr");
		}


		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val(sum + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});

		$("#srb").on('keyup', function () {
			var v = this.value;
			var srb_amount = (sum / 100) * v;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			}
			var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
				credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
				grand_total_for_balance = parseFloat($("#grand_total").val());
				$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
			}
		});


		$("#gst").on('keyup', function () {
			var v = this.value;
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst_amount = (sum / 100) * v;
			var discount = $("#discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			}
			// else if (discount != 0) {
			// 	discount_amount = parseFloat(discount);
			// }
			var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
				credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
				grand_total_for_balance = parseFloat($("#grand_total").val());
				$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
			}
		})

		// $("#discount").on('keyup', function(){
		// 	var v = this.value;
		// 	var srb = $("#srb").val();
		// 	var srb_amount = (sum / 100) * srb;
		// 	var gst = $("#gst").val();
		// 	var gst_amount = (sum / 100) * gst;
		// 	var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		// 	var discount_amount = (amount_before_discount / 100) * v;
		// 	$("#discount_in_val").val(discount_amount.toFixed(2));
		// 	if (!isNaN(v) && v.length != 0){
		// 	$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
		// 	credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
		// 	grand_total_for_balance = parseFloat($("#grand_total").val());
		// 	$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		// 	}
		// })

		$("#discount_in_val").on('keyup', function () {
			
			var v = this.value;
			var srb = $("#srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (sum / 100) * gst;
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			var discount_amount = parseFloat(v);
			var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
			$("#discount").val(discount_in_percentage.toFixed(2));
			if (!isNaN(v) && v.length != 0) {
				$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
				credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
				grand_total_for_balance = parseFloat($("#grand_total").val());
				$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
			}
		})

	});

	// Edit row on edit button click
	$(document).on("click", ".edit-transaction-sale", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 3) {
				$(this).html('<input type="text" style="width:280px;" class="form-control" value="' + $(this).text() + '">');
			}

			if (i === 9) {
				$(this).html('<input type="text" style="width:80px;" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-transaction-sale, .edit-transaction-sale").toggle();
		$(".add-item-sale").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-transaction-sale", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-sale").removeAttr("disabled");

		after_delete();

	});

	function after_delete() {
		var delete_sum = 0;
		$('#new-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				delete_sum += parseFloat(total);
			}
			var srb = $("#srb").val();
			var srb_amount = (delete_sum / 100) * srb;
			var gst = $("#gst").val();
			var gst_amount = (delete_sum / 100) * gst;
			var discount = $("#discount").val();
			var amount_before_discount = parseFloat(delete_sum + srb_amount + gst_amount);
			var discount_amount = (amount_before_discount / 100) * discount;
			$('#grand_total').val(delete_sum + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	}

	$('#new-sale-submit').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#new-sale-table');
		var data = [];
		var sale_id = $('#sale_id').val();
		var credit_days = $('#credit_days').val();
		var customer = $('#customer').val();
		var account_holder = $('#account_holder').val();
		var payment_method = $('#payment_method').val();
		var footer_desc = $('#footer_desc').val();
		var srb = $('#srb').val();
		var gst = $('#gst').val();
		var discount = $('#discount').val();
		var date = $('#date').val();
		var po_no = $('#po_no').val();
		var grn_no = $('#grn_no').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'description': "",
					'width': "",
					'height': "",
					'quantity': "",
					'sqft': "",
					'rate': "",
					'total': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 3) {
						row["description"] = ($(this).find('input').val());
					} else if (i === 5) {
						row["width"] = ($(this).text());
					} else if (i === 6) {
						row["height"] = ($(this).text());
					} else if (i === 7) {
						is_und = ($(this).find('input').val())
						if (typeof is_und == "undefined") {
							row["quantity"] = ($(this).text());
						} else {
							row["quantity"] = ($(this).find('input').val());
						}
					} else if (i === 8) {
						row["sqft"] = ($(this).text());
					} else if (i === 9) {
						row["rate"] = ($(this).find('input').val());
					} else if (i === 10) {
						row["total"] = ($(this).text());
					} else if (i === 11) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/sale/new/',
				data: {
					'sale_id': sale_id,
					'customer': customer,
					'credit_days': credit_days,
					'account_holder': account_holder,
					'payment_method': payment_method,
					'footer_desc': footer_desc,
					'srb': srb,
					'gst': gst,
					"discount": discount,
					'po_no': po_no,
					'grn_no': grn_no,
					'date': date,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (data.result) {
					$.toast().reset('all');
					$.toast({
						heading: 'Submitted Successfully',
						text: 'Yes! check here <a href="/transaction/sale/commercial-print/' + data.header_id + '" target="_blank">' + data.sale_id + '</a>.',
						hideAfter: false,
						icon: 'success',
						'position': 'mid-center'
					})
					setInterval(function () {
						location.reload()
					}, 2000);
				} else {
					$(".disable_on_submit").prop('disabled', false);
					var myToast = $.toast({
						text: data.e,
						hideAfter: false,
						bgColor: '#E01A31',
						'position': 'bottom-left',
						icon: 'error'
					});
				}
			})
	});


	// =============================================================================
	// $('#edit-sale-table tbody tr').each(function() {
	// 	var tdObject = $(this).find('td:eq(10)');
	// 	var total = tdObject.text()
	// 	if (!isNaN(total) && total.length !== 0) {
	// 			sum += parseFloat(total);
	// 	}
	// 	var srb = $("#edit_srb").val();
	// 	var srb_amount = (sum / 100) * srb;
	// 	var gst = $("#edit_gst").val();
	// 	var gst_amount = (sum / 100) * gst;
	// 	var discount = $("#edit_discount").val();
	// 	var discount_amount = 0
	// 	var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
	// 	discount_amount = amount_before_discount * discount / 100
	// 	$("#discount_in_val_edit").val(discount_amount);
	// 	$('#grand_total').val(Math.round(sum + srb_amount + gst_amount - discount_amount).toFixed(2));
	// });

	var sum = 0;
	$('#edit-sale-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(10)');
		var total = tdObject.text()
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}

		var srb = $("#edit_srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst = $("#edit_gst").val();
		var gst_amount = (sum / 100) * gst;
		var discount = $("#edit_discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val_edit").val();
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		} else {
			discount_amount = 0;
		}
		var credit_balance_amount = $("#credit_balance").val()
		$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
		credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
		grand_total_for_balance = parseFloat($("#grand_total").val());
		$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
	});

	// $("#edit_gst").on('keyup', function(){
	// 	var v = this.value;
	// 	var srb = $("#edit_srb").val();
	// 	var srb_amount = (sum / 100) * srb;
	// 	var gst_amount = (sum / 100) * v;
	// 	var discount = $("#edit_discount").val();
	// 	var discount_amount = 0
	// 	var discount_in_val = $("#discount_in_val_edit").val();
	// 	var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
	// 	if (discount_in_val != 0) {
	// 			discount_amount =  discount_in_val;
	// 	}
	// 	console.log(discount_in_val);					
	// 	var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
	// 	$("#edit_discount").val(discount_in_percentage.toFixed(2));
	// 	if (!isNaN(v) && v.length != 0){
	// 	$("#grand_total").val((parseFloat(sum) + srb_amount + gst_amount - discount_in_val).toFixed(2));
	// 	}
	// })


	// $("#edit_srb").on('keyup', function(){
	// 	var v = this.value;
	// 	var gst = $("#edit_gst").val();
	// 	var srb_amount = (sum / 100) * v;
	// 	var gst_amount = (sum / 100) * gst;
	// 	var discount = $("#edit_discount").val();
	// 	var discount_amount = 0
	// 	var discount_in_val = $("#discount_in_val_edit").val();
	// 	var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
	// 	if (discount_in_val != 0) {
	// 			discount_amount =  discount_in_val;
	// 	}
	// 	var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
	// 	$("#edit_discount").val(discount_in_percentage.toFixed(2));
	// 	if (!isNaN(v) && v.length != 0){
	// 	$("#grand_total").val((parseFloat(sum) + srb_amount + gst_amount - discount_in_val).toFixed(2));
	// 	}
	// })

	// $("#discount_in_val").on('keyup', function(){
	// 	var v = this.value;
	// 	var srb = $("#edit_srb").val();
	// 	console.log(isNaN(srb));
	// 	var srb_amount = (sum / 100) * srb;
	// 	var gst = $("#edit_gst").val();
	// 	var gst_amount = (sum / 100) * gst;
	// 	var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
	// 	var discount_amount = parseFloat(v);
	// 	var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
	// 	$("#discount").val(discount_in_percentage.toFixed(2));
	// 	if (!isNaN(v) && v.length != 0){
	// 	$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
	// 	}
	// })

	$(".add-item-sale-edit").click(function () {
		var job_no_sale = $('#job_no_sale_edit').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/edit/${edit_id}`,
				data: {
					'job_no_sale': job_no_sale,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				for (var i = 0; i < data.items.length; i++) {
					if (data.items[i][3] == "sq.ft") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit * parseFloat(data.items[i][6])
					} else if (data.items[i][3] == "sq.inches") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit / 144
						square_fit = square_fit * parseFloat(data.items[i][6])
					}
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + data.items[i][0] + '</td>' +
						'<td>' + data.items[i][1] + '</td>' +
						'<td><input type="text" style="width:280px;" class="form-control"></td>' +
						'<td>sq.ft</td>' +
						'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
						'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
						'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
						'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
						'<td id="rate" ><input type="text" style="width:80px;" class="form-control input_rate_sale_edit"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;">' + data.items[i][3] + '</td>' +
						'<td><a class="delete-transaction-sale-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".add-transaction-sale-edit, .edit-transaction-sale-edit").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");
				}
			});
	});


	$('#job_no_sale_edit').on('keypress', function (e) {

		edit_id = $(this).attr("data-id")
		if (e.which == 13) {
			e.preventDefault();

			var job_no_sale = $('#job_no_sale_edit').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: `/transaction/sale/edit/${edit_id}`,
					data: {
						'job_no_sale': job_no_sale,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					for (var i = 0; i < data.items.length; i++) {
						if (data.items[i][3] == "sq.ft") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit * parseFloat(data.items[i][6])
						} else if (data.items[i][3] == "sq.inches") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit / 144
							square_fit = square_fit * parseFloat(data.items[i][6])
						}
						var index = $("table tbody tr:last-child").index();
						var row = '<tr>' +
							'<td>' + count + '</td>' +
							'<td>' + data.items[i][0] + '</td>' +
							'<td>' + data.items[i][1] + '</td>' +
							'<td><input type="text" style="width:280px;" class="form-control"></td>' +
							'<td>' + data.items[i][3] + '</td>' +
							'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
							'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
							'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
							'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
							'<td id="rate" ><input type="text" style="width:80px;" class="form-control input_rate_sale_edit"></td>' +
							'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
							'<td style="display:none;">' + data.items[i][3] + '</td>' +
							'<td><a class="delete-transaction-sale-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
							'</tr>';
						count++;
						$("table").append(row);
						$("table tbody tr").eq(index + 1).find(".add-transaction-sale-edit, .edit-transaction-sale-edit").toggle();
						$('[data-toggle="tooltip"]').tooltip();
						$('#item_code_sale').val("");
					}
				});
		}
	})

	$(".add-item-x-edit").click(function () {
		var job_no_sale = "";
		var x_stand_edit = $('#x_stand_edit_sale').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/edit/${edit_id}`,
				data: {
					'x_stand_edit': x_stand_edit,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><input type="text" style="width:300px;" class="form-control" value=' + type[0].fields["item_description"] + '></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0.00</td>' +
					'<td id="height">0.00</td>' +
					'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_quantity_x_sale_edit"></td>' +
					'<td id="sqft">0.00</td>' +
					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_x_sale_edit"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;"></td>' +
					'<td><a class="delete-transaction-sale-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".edit-transaction-sale-edit, .add-transaction-sale-edit").toggle();
				$('[data-toggle="tooltip"]').tooltip();
				$('#item_code_sale').val("");
			});
	});


	$('#x_stand_edit_sale').on('keypress', function (e) {
		edit_id = $(this).attr("data-id")

		if (e.which == 13) {
			e.preventDefault();

			var x_stand_edit_sale = $('#x_stand_edit_sale').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: `/transaction/sale/edit/${edit_id}`,
					data: {
						'x_stand_edit': x_stand_edit_sale,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control" value=' + type[0].fields["item_description"] + '></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0.00</td>' +
						'<td id="height">0.00</td>' +
						'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_quantity_x_sale_edit"></td>' +
						'<td id="sqft">0.00</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_x_sale_edit"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;"></td>' +
						'<td><a class="delete-transaction-sale-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-sale-edit, .add-transaction-sale-edit").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");
				});
		}
	})

	$("#edit-sale-table").on('keyup', '.input_rate_sale_edit', function () {
		var input_rate_sale = $(this).val();
		var input_sq_ft = $(this).parents('tr').find('td#sqft').text();

		total = parseFloat(input_rate_sale) * parseFloat(input_sq_ft);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("sq.ft");

		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#edit_srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#edit_gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#edit_discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val_edit").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#edit-sale-table").on('keyup', '.input_quantity_x_sale_edit', function () {
		var input_x_quantity_sale = $(this).val();
		var input_rate_sale = $(this).parents('tr').find('input.input_rate_x_sale_edit').val();
		if (isNaN(input_rate_sale) && input_rate_sale) {
			input_rate_sale = 0
		}
		total = input_rate_sale * parseFloat(input_x_quantity_sale);
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
			var srb = $("#edit_srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#edit_gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#edit_discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val_edit").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#edit-sale-table").on('keyup', '.input_rate_x_sale_edit', function () {
		var input_x_rate_sale = $(this).val();
		var input_x_quantity_sale = $(this).parents('tr').find('input.input_quantity_x_sale_edit').val();
		if (isNaN(input_x_quantity_sale) && input_x_quantity_sale) {
			input_x_quantity_sale = 0
		}
		total = input_x_rate_sale * input_x_quantity_sale;
		var sum = $(this).parents('tr').find('td.sum').text(total.toFixed(2));
		$(this).parents('tr').find('#measurment').text("");

		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}

			var srb = $("#edit_srb").val();
			var srb_amount = (sum / 100) * srb;
			var gst = $("#edit_gst").val();
			var gst_amount = (sum / 100) * gst;
			var discount = $("#edit_discount").val();
			var discount_amount = 0
			var discount_in_val = $("#discount_in_val_edit").val();
			var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

			if (discount_in_val != 0) {
				discount_amount = (amount_before_discount / 100) * discount_in_val;
			} else {
				discount_amount = 0;
			}
			var credit_balance_amount = $("#credit_balance").val()
			$('#grand_total').val((sum + srb_amount + gst_amount - discount_in_val).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		});
	})


	$("#edit_srb").on('keyup', function () {
		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb_amount = (sum / 100) * v;
		var gst = $("#edit_gst").val();
		var gst_amount = (sum / 100) * gst;
		var discount = $("#edit_discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val_edit").val();

		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);

		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		}

		var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)

		$("#edit_discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val((parseFloat(sum) + srb_amount + gst_amount - discount_amount).toFixed(2));
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	});


	$("#edit_gst").on('keyup', function () {
		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb = $("#edit_srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst_amount = (sum / 100) * v;
		var discount = $("#edit_discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val_edit").val();
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		}

		var discount_in_percentage = ((((Math.abs(discount_in_val) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#edit_discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})


	$("#discount_in_val_edit").on('keyup', function () {
		var sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				sum += parseFloat(total);
			}
		})
		var v = this.value;
		var srb = $("#edit_srb").val();
		var srb_amount = (sum / 100) * srb;
		var gst = $("#edit_gst").val();
		var gst_amount = (sum / 100) * gst;
		var amount_before_discount = parseFloat(sum + srb_amount + gst_amount);
		var discount_amount = parseFloat(v);
		var discount_in_percentage = ((((Math.abs(v) + amount_before_discount) / amount_before_discount) * 100) - 100)
		$("#edit_discount").val(discount_in_percentage.toFixed(2));
		if (!isNaN(v) && v.length != 0) {
			$("#grand_total").val(parseFloat(sum) + srb_amount + gst_amount - discount_amount);
			credit_balance_hidden = parseFloat($("#credit_balance_hidden").val());
			grand_total_for_balance = parseFloat($("#grand_total").val());
			$("#credit_balance").val(credit_balance_hidden + grand_total_for_balance);
		}
	})


	// // Add row on add button click
	// $(document).on("click", ".add-transaction-sale-edit", function(){
	// sum = 0;

	// 	var empty = false;
	// 	var input = $(this).parents("tr").find('input[type="text"]');
	// 			input.each(function(){
	// 		if(!$(this).val()){
	// 			$(this).addClass("error");
	// 			empty = true;
	// 		}
	// 		else{
	// 				$(this).removeClass("error");
	// 				}

	// 	});

	// $(this).parents("tr").find(".error").first().focus();
	// if(!empty){
	// 	input.each(function(){
	// 		$(this).parent("td").html($(this).val());
	// 	});
	// 	$(this).parents("tr").find(".add-transaction-sale-edit, .edit-transaction-sale-edit").toggle();
	// 	$(".add-item-sale").removeAttr("disabled");
	// }

	// var check_condition = $($(this).parents("tr").find("#width")).filter(function() {
	// 			check = $(this).text();
	// 			return check;
	// 	}).closest("tr");
	// if (check == "0.00") {
	// 	console.log("Hmza");
	// 	var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
	// 				quantity = $(this).text();
	// 				return quantity;
	// 		}).closest("tr");

	// 	var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 				rate = $(this).text();
	// 				return rate;
	// 		}).closest("tr");

	// 	var total = parseFloat(quantity) * parseFloat(rate)
	// 	console.log(total);
	// 	var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 				$(this).text(total.toFixed(2));
	// 				console.log(this);
	// 				console.log(total);
	// 				return total;
	// 		}).closest("tr");
	// }
	// else {
	// 	var get_sqft = $($(this).parents("tr").find("#sqft")).filter(function() {
	// 			sqft = $(this).text();
	// 			return sqft;
	// 	}).closest("tr");

	// 	var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 				rate = $(this).text();
	// 				return rate;
	// 		}).closest("tr");

	// 	total = parseFloat(sqft) * parseFloat(rate)
	// 	var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 				total = $(this).text(total.toFixed(2));
	// 				return total;
	// 		}).closest("tr");

	// }

	// $('#edit-sale-table tbody tr').each(function() {
	// 		var tdObject = $(this).find('td:eq(10)');
	// 		var total = tdObject.text()
	// 		console.log(total);
	// 		if (!isNaN(total) && total.length !== 0) {
	// 				sum += parseFloat(total);
	// 		}
	// 		console.log(sum);
	// 		$('#grand_total').val(sum.toFixed(2));
	// });

	// });

	// 		// Edit row on edit button click
	// $(document).on("click", ".edit-transaction-sale-edit", function(){
	// $(this).parents("tr").find("td:not(:last-child)").each(function(i){
	// 	if (i === 3) {
	// 		 $(this).html('<input type="text" style="width:280px;" class="form-control" value="' + $(this).text() + '">');
	// 	}

	// 		if (i === 9) {
	// 			 $(this).html('<input type="text" style="width:80px;" class="form-control" value="' + $(this).text() + '">');
	// 		}

	// });
	// $(this).parents("tr").find(".add-transaction-sale-edit, .edit-transaction-sale-edit").toggle();
	// $(".add-item-sale").attr("disabled", "disabled");
	// });

	// Delete row on delete button click
	$(document).on("click", ".delete-transaction-sale-edit", function () {

		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-sale").removeAttr("disabled");
		after_delete_sale_edit();
	});



	function after_delete_sale_edit() {
		var delete_sum = 0;
		$('#edit-sale-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(10)');
			var total = tdObject.text()
			if (!isNaN(total) && total.length !== 0) {
				delete_sum += parseFloat(total);
			}
			var srb = $("#edit_srb").val();
			var srb_amount = (delete_sum / 100) * srb;
			var gst = $("#edit_gst").val();
			var gst_amount = (delete_sum / 100) * gst;
			var discount = $("#discount_in_val_edit").val();
			var amount_before_discount = parseFloat(delete_sum + srb_amount + gst_amount);
			var discount_amount = discount;
			$('#grand_total').val((delete_sum + srb_amount + gst_amount - discount_amount).toFixed(2));
		});
	}




	$('#edit-sale-submit').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#edit-sale-table');
		var data = [];
		var sale_id = $('#sale_id').val();
		var date = $('#date').val();
		var account_holder = $('#account_holder').val();
		var credit_days = $('#credit_days').val();
		var customer = $('#customer_name_sale').val();
		var payment_method = $('#payment_method').val();
		var gst = $('#edit_gst').val();
		var srb = $('#edit_srb').val();
		var po_no = $('#po_no').val();
		var grn_no = $('#grn_no').val();
		var discount = $('#edit_discount').val();
		var footer_desc = $('#footer_desc').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'id': "",
					'description': "",
					'width': "",
					'height': "",
					'quantity': "",
					'sqft': "",
					'rate': "",
					'total': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["id"] = ($(this).text());
					}
					if (i === 3) {
						row["description"] = ($(this).find('input').val());
					} else if (i === 5) {
						row["width"] = ($(this).text());
					} else if (i === 6) {
						row["height"] = ($(this).text());
					} else if (i === 7) {
						is_und = ($(this).find('input').val())
						if (typeof is_und == "undefined") {
							row["quantity"] = ($(this).text());
						} else {
							row["quantity"] = ($(this).find('input').val());
						}
					} else if (i === 8) {
						row["sqft"] = ($(this).text());
					} else if (i === 9) {
						row["rate"] = ($(this).find('input').val());
					} else if (i === 10) {
						row["total"] = ($(this).text());
					} else if (i === 11) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/edit/${edit_id}`,
				data: {
					'sale_id': sale_id,
					'customer': customer,
					'account_holder': account_holder,
					'credit_days': credit_days,
					'payment_method': payment_method,
					'footer_desc': footer_desc,
					'gst': gst,
					'srb': srb,
					'discount': discount,
					'po_no': po_no,
					'grn_no': grn_no,
					'date': date,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (data.result) {
					$.toast().reset('all');
					$.toast({
						heading: 'Updated Successfully',
						text: 'Yes! check here <a href="/transaction/commercial-print/' + data.header_id + '" target="_blank">' + data.sale_id + '</a>.',
						hideAfter: false,
						icon: 'success',
						'position': 'mid-center'
					})
					setInterval(function () {
						location.reload()
					}, 2000);
				} else {
					$(".disable_on_submit").prop('disabled', false);
					var myToast = $.toast({
						text: data.e,
						hideAfter: false,
						bgColor: '#E01A31',
						'position': 'bottom-left',
						icon: 'error'
					});
				}
			})
	});


	// // ==================================================================================================================================


	// EDIT PURCHASE RETURN

	// Add row on add button click
	$(document).on("click", ".add-purchase-return", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-purchase-return, .edit-purchase-return").toggle();
		}
	});


	// Edit row on edit button click
	$(document).on("click", ".edit-purchase-return", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 4) {
				$(this).html('<input type="text" class="form-control form-control-sm" value="' + $(this).text() + '">');
			}
		});
		$(this).parents("tr").find(".add-purchase-return, .edit-purchase-return").toggle();
	});


	// Delete row on delete button click
	$(document).on("click", ".delete-purchase-return", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-sale").removeAttr("disabled");
	});

	//SUBMIT EDIT MRN SUPPLIER

	//updating data into supplier mrn using ajax request
	$('#new-purchase-return-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-purchase-return-table');
		var supplier = $('#supplier_purchase_return').val();
		var payment_method = $('#payment_purchase_return').val();
		var description = $('#desc_purchase_return').val();
		console.log(supplier);
		var data = [];
		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'item_name': "",
					'item_description': "",
					'quantity': "",
					'unit': "",
					'price': "",
					'sales_tax': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 2) {
						row["item_name"] = ($(this).text());
					} else if (i === 3) {

						row["item_description"] = ($(this).text());
					} else if (i === 4) {
						row["quantity"] = ($(this).text());

					} else if (i === 5) {
						row["unit"] = ($(this).text());
					} else if (i === 6) {
						row["price"] = ($(this).text());
					} else if (i === 7) {
						row["sales_tax"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/purchase/return/${edit_id}`,
				data: {
					'supplier': supplier,
					'payment_method': payment_method,
					'description': description,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done() {
				alert("Updated");
				location.reload();
			})
	});

	// //=======================================================================================
	//
	// // ==================================================================================================================================
	// 							// EDIT PURCHASE RETURN

	// Add row on add button click
	$(document).on("click", ".add-sale-return", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-sale-return, .edit-sale-return").toggle();
		}
	});


	// Edit row on edit button click
	$(document).on("click", ".edit-sale-return", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 4) {
				$(this).html('<input type="text" class="form-control form-control-sm" value="' + $(this).text() + '">');
			}
		});
		$(this).parents("tr").find(".add-sale-return, .edit-sale-return").toggle();
	});

	//SUBMIT EDIT MRN SUPPLIER

	//updating data into supplier mrn using ajax request
	$('#new-sale-return-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-sale-return-table');
		var customer = $('#customer_sale_return').val();
		var payment_method = $('#payment_sale_return').val();
		var description = $('#desc_sale_return').val();
		var data = [];
		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'item_name': "",
					'item_description': "",
					'quantity': "",
					'unit': "",
					'price': "",
					'sales_tax': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 2) {
						row["item_name"] = ($(this).text());
					} else if (i === 3) {

						row["item_description"] = ($(this).text());
					} else if (i === 4) {
						row["quantity"] = ($(this).text());

					} else if (i === 5) {
						row["unit"] = ($(this).text());
					} else if (i === 6) {
						row["price"] = ($(this).text());
					} else if (i === 7) {
						row["sales_tax"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/return/${edit_id}`,
				data: {
					'customer': customer,
					'payment_method': payment_method,
					'description': description,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done() {
				alert("Updated");
				location.reload();
			})
	});

	//=======================================================================================


	$(".add-item-sale-edit").click(function () {
		console.log("click");
		var item_code_sale = $('#item_code_sale_edit').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/edit/${edit_id}`,
				data: {
					'item_code_sale': item_code_sale,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var type = JSON.parse(data.row);
				var index = $("table tbody tr:last-child").index();
				total_amount = (type[0].fields['unit_price'] * type[0].fields['quantity']);
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields['product_code'] + '</td>' +
					'<td>' + type[0].fields['product_name'] + '</td>' +
					'<td id="desc" ><input type="text" style="width:280px;" value="' + type[0].fields['product_name'] + '" class="form-control"></td>' +
					'<td id="quantity_edit" ><input type="text" class="form-control" value=""></td>' +
					'<td><input type="text" class="form-control" value=""></td>' +
					'<td id="price_edit" ><input type="text" class="form-control" value=""></td>' +
					'<td id="value_of_goods_edit" >0.00</td>' +
					'<td id="sales_tax_edit"><input type="text" class="form-control" value=""></td>' +
					'<td id="sales_tax_amount_edit">0.00</td>' +
					'<td><a class="add-sale-edit" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-sale-edit" title="Edit" data-toggle="tooltip" id="edit_sale"><i class="material-icons">&#xE254;</i></a><a class="delete-sale-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-sale-edit, .edit-sale-edit").toggle();
				$('[data-toggle="tooltip"]').tooltip();
			});
	});


	// Add row on add button click
	$(document).on("click", ".add-sale-edit", function () {
		sum = 0;
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-sale-edit, .edit-sale-edit").toggle();
			$(".add-item-sale").removeAttr("disabled");
		}
		console.log($(this));
		var get_price = $($(this).parents("tr").find("#price_edit")).filter(function () {
			price = $(this).text();
			console.log(price);
			return price
		}).closest("tr");

		var get_quantity = $($(this).parents("tr").find("#quantity_edit")).filter(function () {
			quantity = $(this).text();
			return quantity
		}).closest("tr");
		console.log(quantity);
		var set_valueOfGoods = $($(this).parents("tr").find("#value_of_goods_edit")).filter(function () {
			value_of_goods = quantity * price
			$(this).text(value_of_goods.toFixed(2))
			return value_of_goods;
		}).closest("tr");

		var get_salesTax = $($(this).parents("tr").find("#sales_tax_edit")).filter(function () {
			sales_tax = value_of_goods * $(this).text();
			sales_tax = sales_tax / 100
			return sales_tax;
		}).closest("tr");

		var set_salesTax = $($(this).parents("tr").find("#sales_tax_amount_edit")).filter(function () {
			$(this).text(sales_tax.toFixed(2));
			return sales_tax;
		}).closest("tr");

		var set_total = $($(this).parents("tr").find("#total")).filter(function () {
			total = value_of_goods + sales_tax
			$(this).text(total.toFixed(2));
			return sales_tax;
		}).closest("tr");

		$($(this).parents("tr").find("#total")).each(function () {
			var value = $(this).text();
			// add only if the value is number
			if (!isNaN(value) && value.length != 0) {
				console.log(value);
			}
		});

		$('#new-sale-table > tbody  > tr').each(function () {
			sum = sum + parseFloat($(this).find('td#total').text());
		});

	});

	// Edit row on edit button click
	$(document).on("click", ".edit-sale-edit", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 4) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 5) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 8) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-sale-edit, .edit-sale-edit").toggle();
		$(".add-item-sale").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-sale-edit", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-sale").removeAttr("disabled");
	});

	$('#cartage_amount').on('keyup', function (e) {
		var i = this.value;
		var at = $('#additional_tax').val()
		if (!isNaN(i) && i.length != 0) {
			if (!isNaN(at)) {
				var a = sum
				var v = parseFloat(a) + parseFloat(i) + parseFloat(at)
				$('#last_grand_total').val(v.toFixed(2));
			} else {
				var a = sum
				var v = parseFloat(a) + parseFloat(i)
				$('#last_grand_total').val(v.toFixed(2));
			}
		} else {
			if (!isNaN(at)) {
				sum = parseFloat(at) + sum;
				$('#last_grand_total').val(sum.toFixed(2));
			} else {
				$('#last_grand_total').val(sum);
			}
		}
	});

	$('#additional_tax').on('keyup', function () {
		var i = this.value;
		var ac = $('#cartage_amount').val()
		if (!isNaN(i) && i.length != 0) {
			if (!isNaN(ac)) {
				var a = sum
				var v = parseFloat(a) + parseFloat(i) + parseFloat(ac)
				$('#last_grand_total').val(v.toFixed(2));
			} else {
				var a = sum
				var v = parseFloat(a) + parseFloat(i)
				$('#last_grand_total').val(v.toFixed(2));
			}
		} else {
			if (!isNaN(ac)) {
				sum = parseFloat(ac) + sum;
				$('#last_grand_total').val(sum.toFixed(2));
			} else {
				$('#last_grand_total').val(sum);
			}
		}

	})



	// =============================================================================
	// $(".add-item-purchase-edit").click(function(){
	// var item_code_purchase_edit = $('#item_code_purchase_edit').val();
	//
	// 	req =	$.ajax({
	// 		 headers: { "X-CSRFToken": getCookie("csrftoken") },
	// 		 type: 'POST',
	// 		 url : '/transaction/sale/new/',
	// 		 data:{
	// 			 'item_code_purchase_edit': item_code_purchase_edit,
	// 		 },
	// 		 dataType: 'json'
	// 	 })
	// 	 .done(function done(data){
	// 		 console.log(data.items);
	// 		var index = $("table tbody tr:last-child").index();
	// 				var row = '<tr>' +
	// 						'<td>'+count+'</td>' +
	// 						'<td>'+data.items[i][0]+'</td>'+
	// 						'<td>'+data.items[i][1]+'</td>'+
	// 						'<td><pre>'+data.items[i][2]+'</pre></td>'+
	// 						'<td>sq.ft</td>'+
	// 						'<td id="width">'+data.items[i][4].toFixed(2)+'</td>'+
	// 						'<td id="height">'+data.items[i][5].toFixed(2)+'</td>'+
	// 						'<td id="quantity">'+data.items[i][6].toFixed(2)+'</td>'+
	// 						'<td id="sqft">'+square_fit.toFixed(2)+'</td>'+
	// 						'<td id="rate" ><input type="text" style="width:80px;" class="form-control"></td>' +
	// 						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
	// 						'<td style="display:none;">'+data.items[i][3]+'</td>'+
	// 			'<td><a class="add-purchase-edit" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-purchase-edit" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-purchase-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
	// 				'</tr>';
	// 				count++;
	// 			$("table").append(row);
	// 		$("table tbody tr").eq(index + 1).find(".add-purchase-edit, .edit-purchase-edit").toggle();
	// 				$('[data-toggle="tooltip"]').tooltip();
	// 				$('#item_code_purchase_edit').val("");
	// 	});
	//
	// });
	//
	// // Add row on add button click
	// $(document).on("click", ".add-purchase-edit", function(){
	// 	$('#sel').prop('disabled', 'disabled');
	// sum = 0;
	//
	// 	var empty = false;
	// 	var input = $(this).parents("tr").find('input[type="text"]');
	// 			input.each(function(){
	// 		if(!$(this).val()){
	// 			$(this).addClass("error");
	// 			empty = true;
	// 		}
	// 		else{
	// 				$(this).removeClass("error");
	// 				}
	//
	// 	});
	//
	// $(this).parents("tr").find(".error").first().focus();
	// if(!empty){
	// 	input.each(function(){
	// 		$(this).parent("td").html($(this).val());
	// 	});
	// 	$(this).parents("tr").find(".add-purchase-edit, .edit-purchase-edit").toggle();
	// 	$(".add-item-sale").removeAttr("disabled");
	// }
	//
	// var get_sqft = $($(this).parents("tr").find("#sqft")).filter(function() {
	// 		sqft = $(this).text();
	// 		return sqft;
	// }).closest("tr");
	//
	// var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
	// 			rate = $(this).text();
	// 			return rate;
	// 	}).closest("tr");
	//
	//
	// total = parseFloat(sqft) * parseFloat(rate)
	//
	// var get_total = $($(this).parents("tr").find("#total")).filter(function() {
	// 			total = $(this).text(total.toFixed(2));
	// 			return total;
	// 	}).closest("tr");
	//
	// });
	//
	// 		// Edit row on edit button click
	// $(document).on("click", ".edit-purchase-edit", function(){
	// 	$('#sel').prop('disabled', false);
	// $(this).parents("tr").find("td:not(:last-child)").each(function(i){
	// 	if (i === 5) {
	// 		 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 	}
	// 	if (i === 6) {
	// 		 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 	}
	// 	if (i === 7) {
	// 		 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 	}
	// 	if (i === 9) {
	// 		 $(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
	// 	}
	//
	// });
	// $(this).parents("tr").find(".add-purchase-edit, .edit-purchase-edit").toggle();
	// $(".item_code_purchase_edit").attr("disabled", "disabled");
	// });
	//
	// // Delete row on delete button click
	// $(document).on("click", ".delete-purchase-edit", function(){
	// var row =  $(this).closest('tr');
	// var siblings = row.siblings();
	// siblings.each(function(index) {
	// $(this).children('td').first().text(index + 1);
	// });
	// $(this).parents("tr").remove();
	// $(".item_code_purchase_edit").removeAttr("disabled");
	// });
	//
	//
	//
	//
	// $('#new-sale-submit').on('submit',function(e){
	// e.preventDefault();
	// var table = $('#new-sale-table');
	// var data = [];
	// var sale_id = $('#sale_id').val();
	// var follow_up = $('#follow_up').val();
	// var customer = $('#customer').val();
	// var payment_method = $('#payment_method').val();
	// var footer_desc = $('#footer_desc').val();
	//
	//
	// table.find('tr').each(function (i, el){
	// if(i != 0)
	// {
	// var $tds = $(this).find('td');
	// var row = {
	// 	'item_code' : "",
	// 	'width' : "",
	// 	'height' : "",
	// 	'quantity' : "",
	// 	'rate' : "",
	// 	'total': "",
	// 	'measurment' : "",
	// };
	// $tds.each(function(i, el){
	// 	if (i === 1) {
	// 			row["item_code"] = ($(this).text());
	// 			console.log($(this).text());
	// 	}
	// 	else if (i === 5) {
	// 			row["width"] = ($(this).text());
	// 	}
	// 	else if (i === 6) {
	// 			row["height"] = ($(this).text());
	// 	}
	// 	else if (i === 7) {
	// 			row["quantity"] = ($(this).text());
	// 	}
	// 	else if (i === 9) {
	// 			row["rate"] = ($(this).text());
	// 	}
	// 	else if (i === 10) {
	// 			row["total"] = ($(this).text());
	// 			console.log($(this).text());
	// 	}
	// 	else if (i === 11) {
	// 			row["measurment"] = ($(this).text());
	// 			console.log($(this).text());
	// 	}
	// });
	// data.push(row);
	// }
	// });
	//
	// req =	$.ajax({
	// 	headers: { "X-CSRFToken": getCookie("csrftoken") },
	// 	type: 'POST',
	// 	url : '/transaction/sale/new/',
	// 	data:{
	// 		'sale_id': sale_id,
	// 		'customer': customer,
	// 		'follow_up': follow_up,
	// 		'payment_method': payment_method,
	// 		'footer_desc': footer_desc,
	// 		'items': JSON.stringify(data),
	// 	},
	// 	dataType: 'json'
	// })
	// .done(function done(){
	// 	alert("Sales Created");
	// 	location.reload();
	// })
	// });
	//

	// // ==================================================================================================================================

	$('#edit-sale-return-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-sale-return-table');
		var data = [];
		var sale_id = $('#sale_return_id').val();
		var customer = $('#customer_sale_return_name').val();
		console.log(sale_id);
		var payment_method = $('#payment_method').val();
		var footer_desc = $('#desc_sale_return').val();


		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'item_name': "",
					'item_description': "",
					'quantity': "",
					'unit': "",
					'price': "",
					'sales_tax': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 2) {
						row["item_name"] = ($(this).text());
					} else if (i === 3) {
						row["item_description"] = ($(this).text());
					} else if (i === 4) {
						row["quantity"] = ($(this).text());
					} else if (i === 5) {
						row["unit"] = ($(this).text());
					} else if (i === 6) {
						row["price"] = ($(this).text());
					} else if (i === 7) {
						row["sales_tax"] = ($(this).text());
					}
				});
				data.push(row);
			}
		});

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/sale/return/edit/${edit_id}`,
				data: {
					'sale_id': sale_id,
					'customer': customer,
					'payment_method': payment_method,
					'footer_desc': footer_desc,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done() {
				alert("Sale Return Updated");
				location.reload();
			})
	});

	// ================================================================================

	$.fn.extend({
		treed: function (o) {

			var openedClass = 'fa fa-minus';
			var closedClass = 'fa fa-plus';

			if (typeof o != 'undefined') {
				if (typeof o.openedClass != 'undefined') {
					openedClass = o.openedClass;
				}
				if (typeof o.closedClass != 'undefined') {
					closedClass = o.closedClass;
				}
			};

			//initialize each of the top levels
			var tree = $(this);
			tree.addClass("tree");
			tree.find('li').has("ul").each(function () {
				var branch = $(this); //li with children ul
				branch.prepend("<i class='indicator glyphicon " + closedClass + "'></i>");
				branch.addClass('branch');
				branch.on('click', function (e) {
					if (this == e.target) {
						var icon = $(this).children('i:first');
						icon.toggleClass(openedClass + " " + closedClass);
						$(this).children().children().toggle();
					}
				})
				branch.children().children().toggle();
			});
			//fire event from the dynamically added icon
			tree.find('.branch .indicator').each(function () {
				$(this).on('click', function () {
					$(this).closest('li').click();
				});
			});
			//fire event to open branch if the li contains an anchor instead of text
			tree.find('.branch>a').each(function () {
				$(this).on('click', function (e) {
					$(this).closest('li').click();
					e.preventDefault();
				});
			});
			//fire event to open branch if the li contains a button instead of text
			tree.find('.branch>button').each(function () {
				$(this).on('click', function (e) {
					$(this).closest('li').click();
					e.preventDefault();
				});
			});
		}
	});


	$(".add-item-jv").click(function () {
		var account_title = $('#account_title').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + data.account_id + '</td>' +
					'<td>' + data.account_title + '</td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><a class="add-jv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-jv, .edit-jv").toggle();
				$('[data-toggle="tooltip"]').tooltip();

			})
	});


	// Add row on add button click
	$(document).on("click", ".add-jv", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-jv, .edit-jv").toggle();
			$(".add-item-jv").removeAttr("disabled");
		}
	});


	// Edit row on edit button click
	$(document).on("click", ".edit-jv", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-jv, .edit-jv").toggle();
		$(".add-item-jv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-jv", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-jv").removeAttr("disabled");
	});



	$('#add-jv-form').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#new-jv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var doc_no = $('#doc_no').val();
		var doc_date = $('#doc_date').val();
		var description = $('#description').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'account_id': "",
					'account_title': "",
					'debit': "",
					'credit': "",
				};
				$tds.each(function (i, el) {
					if (i === 0) {
						row["account_id"] = ($(this).text());
					}
					if (i === 1) {
						row["account_title"] = ($(this).text());
					} else if (i === 2) {
						row["debit"] = ($(this).text());
						debit = debit + parseFloat(($(this).text()));
					} else if (i === 3) {
						row["credit"] = ($(this).text());
						credit = credit + parseFloat(($(this).text()));
					}
				});
				data.push(row);
			}
		});
		if (debit == credit) {
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/journal_voucher/new',
					data: {
						'doc_no': doc_no,
						'doc_date': doc_date,
						'description': description,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result) {

						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/jv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				})
		} else {
			$(".disable_on_submit").prop('disabled', false);
			var myToast = $.toast({
				text: "Debit and Credit sides are not same",
				hideAfter: false,
				bgColor: '#E01A31',
				'position': 'bottom-left',
				icon: 'error'
			});
		}

	});


	$(".edit-item-jv").click(function () {
		var account_title = $('#account_title').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				console.log(data);
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + data.account_id + '</td>' +
					'<td>' + data.account_title + '</td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><a class="add-jv-edit" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jv-edit" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jv-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-jv-edit, .edit-jv-edit").toggle();
				$('[data-toggle="tooltip"]').tooltip();
			})
	});


	// Add row on add button click
	$(document).on("click", ".add-jv-edit", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-jv-edit, .edit-jv-edit").toggle();
			$(".edit-item-jv").removeAttr("disabled");
		}
	});


	// Edit row on edit button click
	$(document).on("click", ".edit-jv-edit", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-jv-edit, .edit-jv-edit").toggle();
		$(".edit-item-jv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-jv-edit", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".edit-item-jv").removeAttr("disabled");
	});



	$('#edit-jv-form').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		var table = $('#edit-jv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var doc_no = $('#doc_no').val();
		var doc_date = $('#doc_date').val();
		var description = $('#description').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'account_id': "",
					'account_title': "",
					'debit': "",
					'credit': "",
				};
				$tds.each(function (i, el) {
					if (i === 0) {
						row["account_id"] = ($(this).text());
					}
					if (i === 1) {
						row["account_title"] = ($(this).text());
					} else if (i === 2) {
						row["debit"] = ($(this).text());
						debit = debit + parseFloat(($(this).text()));
					} else if (i === 3) {
						row["credit"] = ($(this).text());
						credit = credit + parseFloat(($(this).text()));
					}
				});
				data.push(row);
			}
		});
		if (debit == credit) {
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: `/transaction/journal_voucher/edit/${edit_id}`,
					data: {
						'doc_no': doc_no,
						'doc_date': doc_date,
						'description': description,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result) {

						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/jv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				})
		} else {
			$(".disable_on_submit").prop('disabled', false);
			var myToast = $.toast({
				text: "Debit and Credit sides are not same",
				hideAfter: false,
				bgColor: '#E01A31',
				'position': 'bottom-left',
				icon: 'error'
			});
		}

	});


	//Initialization of treeviews

	$('#tree1').treed();



	// ===============================================================================
	// JOB ORDER

	$(".add-item-jo").click(function () {
		var item_code = $('#item_code_jo').val();
		console.log(item_code);
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/job_order/new/',
				data: {
					'item_code': item_code,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var type = JSON.parse(data.row);
				console.log(type);
				// Append table with add row form on add new button click
				$(this).attr("disabled", "disabled");
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields['item_code'] + '</td>' +
					'<td>' + type[0].fields['item_name'] + '</td>' +
					'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
					'<td id="" width="150px"><select id="sel" class="form-control" style=" height:35px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
					'<td id="width"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="height"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="quantity"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="square_fit">0.00</td>' +
					'<td id="measurment" style="display:none;">1</td>' +
					'<td><a class="add-jo" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jo" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jo" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-jo, .edit-jo").toggle();
				$('[data-toggle="tooltip"]').tooltip();
			});
		$('#item_code_jo').val("");
		$(".add-item-jo").attr("disabled", "disabled");
		$(".has_id").attr("disabled", "disabled");
	});

	// Add row on add button click
	$(document).on("click", ".add-jo", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});


		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-jo, .edit-jo").toggle();
			$(".add-item-jo").removeAttr("disabled");
			$(".has_id").removeAttr("disabled");
		}

		var meas;
		$('#new-jo-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(4)'); //locate the <td> holding select;
			var selectObject = tdObject.find("select"); //grab the <select> tag assuming that there will be only single select box within that <td>
			meas = selectObject.val(); // get the selected country from current <tr>
		});

		var get_height = $($(this).parents("tr").find("#height")).filter(function () {
			height = $(this).text();
			return height
		}).closest("tr");

		var get_width = $($(this).parents("tr").find("#width")).filter(function () {
			width = $(this).text();
			return width
		}).closest("tr");


		var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function () {
			quantity = $(this).text();
			return quantity
		}).closest("tr");

		if (meas === "sq.ft") {
			square_fit = parseFloat(width) * parseFloat(height);
			square_fit = square_fit * parseFloat(quantity)
			var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function () {
				$(this).text(square_fit.toFixed(2));
				return square_fit
			}).closest("tr");
			var measurment = $($(this).parents("tr").find("#measurment")).filter(function () {
				$(this).text("sq.ft");
				return measurment
			}).closest("tr");
		} else if (meas === "sq.inches") {
			square_fit = parseFloat(width) * parseFloat(height)
			square_fit = square_fit / 144
			square_fit = square_fit * parseFloat(quantity)
			var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function () {
				$(this).text(square_fit.toFixed(2));
				return square_fit
			}).closest("tr");
			var measurment = $($(this).parents("tr").find("#measurment")).filter(function () {
				$(this).text("sq.inches");
				return measurment
			}).closest("tr");
			$('#meas').prop('disabled', 'disabled');
		}





	});

	// Edit row on edit button click
	$(document).on("click", ".edit-jo", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 5) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 6) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 7) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
		});
		$(this).parents("tr").find(".add-jo, .edit-jo").toggle();
		$(".add-item-jo").attr("disabled", "disabled");
		$(".has_id").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-jo", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-jo").removeAttr("disabled");
	});

	//NEW RFQ SUPPLIER END

	$('#new-jo-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-jo-table');
		var data = [];
		var client_name = $('#client_name').val();
		var file_name = $('#file_name').val();
		var delivery_date = $('#delivery_date').val();
		var remarks = $('#remarks').val();
		var meas = $('#meas').find(":selected").text();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'item_code': "",
					'item_name': "",
					'item_description': "",
					'width': "",
					'height': "",
					'quantity': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["item_code"] = ($(this).text());
					}
					if (i === 2) {
						row["item_name"] = ($(this).text());
					} else if (i === 3) {
						row["item_description"] = ($(this).text());
					} else if (i === 5) {
						row["width"] = ($(this).text());
					} else if (i === 6) {
						row["height"] = ($(this).text());
					} else if (i === 7) {
						row["quantity"] = ($(this).text());
					} else if (i === 9) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);

			}
		});

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/job_order/new/',
				data: {
					'client_name': client_name,
					'file_name': file_name,
					'delivery_date': delivery_date,
					'remarks': remarks,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (data.result != "success") {
					alert(data.result)
				} else {
					alert("Job Order Submitted");
					location.reload();
				}
			})
	});


	//EDIT JOB ORDER
	$(".edit-item-jo").click(function () {
		var item_code = $('#item_code_jo_edit').val();
		console.log(item_code);
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/job_order/edit/${edit_id}`,
				data: {
					'item_code': item_code,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var type = JSON.parse(data.row);
				console.log(type);
				// Append table with add row form on add new button click
				$(this).attr("disabled", "disabled");
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td style="display:none;">' + type[0]['pk'] + '</td>' +
					'<td>' + type[0].fields['item_code'] + '</td>' +
					'<td>' + type[0].fields['item_name'] + '</td>' +
					'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
					'<td id="" width="150px"><select id="sel" class="form-control" style=" height:35px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
					'<td id="width"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="height"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="quantity"><input type="text" style="width:60px;" class="form-control" value=""></td>' +
					'<td id="square_fit">0.00</td>' +
					'<td id="measurment" style="display:none;"></td>' +
					'<td><a class="add-jo-edit" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jo-edit" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jo-edit" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-jo-edit, .edit-jo-edit").toggle();
				$('[data-toggle="tooltip"]').tooltip();
			});
		$('#item_code_jo').val("");
		$(".edit-item-jo").attr("disabled", "disabled");
		$(".has_id").attr("disabled", "disabled");
	});

	// Add row on add button click
	$(document).on("click", ".add-jo-edit", function () {
		$('#sel').prop('disabled', 'disabled');
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});




		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-jo-edit, .edit-jo-edit").toggle();
			$(".add-item-jo").removeAttr("disabled");
			$(".has_id").removeAttr("disabled");
		}

		var meas;
		$('#edit-jo-table tbody tr').each(function () {
			var tdObject = $(this).find('td:eq(5)'); //locate the <td> holding select;
			var selectObject = tdObject.find("select"); //grab the <select> tag assuming that there will be only single select box within that <td>
			meas = selectObject.val(); // get the selected country from current <tr>
		});

		var get_height = $($(this).parents("tr").find("#height")).filter(function () {
			height = $(this).text();
			return height
		}).closest("tr");
		console.log(height);

		var get_width = $($(this).parents("tr").find("#width")).filter(function () {
			width = $(this).text();
			return width
		}).closest("tr");


		var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function () {
			quantity = $(this).text();
			return quantity
		}).closest("tr");

		console.log(meas);
		if (meas === "sq.ft") {
			square_fit = parseFloat(width) * parseFloat(height);
			square_fit = square_fit * parseFloat(quantity)
			var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function () {
				$(this).text(square_fit.toFixed(2));
				return square_fit
			}).closest("tr");
			var measurment = $($(this).parents("tr").find("#measurment")).filter(function () {
				$(this).text("sq.ft");
				return measurment
			}).closest("tr");
		} else if (meas === "sq.inches") {
			square_fit = parseFloat(width) * parseFloat(height)
			square_fit = square_fit / 144
			square_fit = square_fit * parseFloat(quantity)
			var set_square_fit = $($(this).parents("tr").find("#square_fit")).filter(function () {
				$(this).text(square_fit.toFixed(2));
				return square_fit
			}).closest("tr");
			var measurment = $($(this).parents("tr").find("#measurment")).filter(function () {
				$(this).text("sq.inches");
				return measurment
			}).closest("tr");
			$('#meas').prop('disabled', 'disabled');
		}





	});

	// Edit row on edit button click
	$(document).on("click", ".edit-jo-edit", function () {
		$('#sel').prop('disabled', false);
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 6) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 7) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 8) {
				$(this).html('<input type="text" style="width:60px;" class="form-control" value="' + $(this).text() + '">');
			}
		});
		$(this).parents("tr").find(".add-jo-edit, .edit-jo-edit").toggle();
		$(".add-item-jo").attr("disabled", "disabled");
		$(".has_id").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-jo-edit", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-jo").removeAttr("disabled");
	});

	//NEW RFQ SUPPLIER END

	$('#edit-jo-submit').on('submit', function (e) {
		e.preventDefault();
		var table = $('#edit-jo-table');
		var data = [];
		var client_name = $('#client_name').val();
		var file_name = $('#file_name').val();
		var delivery_date = $('#delivery_date').val();
		var remarks = $('#remarks').val();
		var meas = $('#meas').find(":selected").text();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'id': "",
					'width': "",
					'height': "",
					'quantity': "",
					'measurment': "",
				};
				$tds.each(function (i, el) {
					if (i === 1) {
						row["id"] = ($(this).text());
					} else if (i === 6) {
						row["width"] = ($(this).text());
					} else if (i === 7) {
						row["height"] = ($(this).text());
					} else if (i === 8) {
						row["quantity"] = ($(this).text());
					} else if (i === 10) {
						row["measurment"] = ($(this).text());
					}
				});
				data.push(row);
				console.log(row);
			}
		});
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: `/transaction/job_order/edit/${edit_id}`,
				data: {
					'client_name': client_name,
					'file_name': file_name,
					'delivery_date': delivery_date,
					'remarks': remarks,
					'items': JSON.stringify(data),
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (data.result != "success") {
					alert(data.result)
				} else {
					alert("Job Order Updated");
					location.reload();
				}
			})
	});

	// ===============================================================================

	$(".add-item-bpv").click(function () {
		var account_title = $('#account_title').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + data.account_id + '</td>' +
					'<td>' + data.account_title + '</td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td width="100px"><a class="add-bpv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-bpv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a> <a class="delete-bpv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-bpv, .edit-bpv").toggle();
				$('[data-toggle="tooltip"]').tooltip();

			})
	});


	// Add row on add button click
	$(document).on("click", ".add-bpv", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-bpv, .edit-bpv").toggle();
			$(".add-item-jv").removeAttr("disabled");
		}
	});


	$(document).on("click", ".edit-bpv", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-bpv, .edit-bpv").toggle();
		$(".add-item-jv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-bpv", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-jv").removeAttr("disabled");
	});



	$('#new-jv-form-bpv').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-bpv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var doc_no = $('#doc_no').val();
		var doc_date = $('#doc_date').val()
		var cheque_no = $('#cheque_no').val();;
		var cheque_date = $('#cheque_date').val();
		var description = $('#description').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'account_id': "",
					'account_title': "",
					'debit': "",
					'credit': "",
				};
				$tds.each(function (i, el) {
					if (i === 0) {
						row["account_id"] = ($(this).text());
					}
					if (i === 1) {
						row["account_title"] = ($(this).text());
					} else if (i === 2) {
						row["debit"] = ($(this).text());
						debit = debit + parseFloat(($(this).text()));
					} else if (i === 3) {
						row["credit"] = ($(this).text());
						credit = credit + parseFloat(($(this).text()));
					}
				});
				data.push(row);
			}
		});
		if (debit == credit) {
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/bank_payment_voucher/new',
					data: {
						'doc_no': doc_no,
						'doc_date': doc_date,
						'cheque_no': cheque_no,
						'cheque_date': cheque_date,
						'description': description,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result != "success") {
						alert(data.result)
					} else {
						alert("Voucher Submitted");
						location.reload();
					}
				})
		} else {
			alert("Debit and Credit sides are not same");
		}

	});


	$(".add-item-cpv").click(function () {
		var account_title = $('#account_title').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + data.account_id + '</td>' +
					'<td>' + data.account_title + '</td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td width="100px"><a class="add-cpv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-cpv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a> <a class="delete-cpv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-cpv, .edit-cpv").toggle();
				$('[data-toggle="tooltip"]').tooltip();

			})
	});


	// Add row on add button click
	$(document).on("click", ".add-cpv", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-cpv, .edit-cpv").toggle();
			$(".add-item-cpv").removeAttr("disabled");
		}
	});


	$(document).on("click", ".edit-cpv", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-cpv, .edit-cpv").toggle();
		$(".add-item-cpv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-cpv", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-cpv").removeAttr("disabled");
	});

	var check = 0;
	$(':checkbox').click(function () {
		$('#invoice_no:text').attr('disabled', !this.checked)
		$('#invoice_no:text').prop('required', true);
	});

	$(".load-invoices").click(function () {
		var invoice_no = $('#invoice_no').val()
		console.log(invoice_no);
		if ($('#box').prop("checked") == true) {
			var check = 1;
		} else {
			check = 0
		}
		var account_title = $('#account_title').find(":selected").text();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'check': check,
					'invoice_no': invoice_no,
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var balance_amount = 0;
				var parent_amount = $('#amount').val();
				var index = $("table tbody tr:last-child").index();
				for (var i = 0; i < data.pi.length; i++) {
					b_amount = parseFloat(data.pi[i][4]) - parseFloat(data.pi[i][5])
					if (parent_amount > 0) {
						is_abs = parent_amount - parseFloat(b_amount)
						if (parent_amount > parseFloat(b_amount)) {
							balance_amount = 0.00;
						} else {
							parent_amount = parent_amount - parseFloat(b_amount)
							balance_amount = Math.abs(parent_amount)
						}
						var row = '<tr>' +
							'<td>6</td>' +
							'<td>Cash</td>' +
							'<td>' + data.pi[i][2] + '</td>' +
							'<td>' + b_amount.toFixed(2) + '</td>' +
							'<td>0.00</td>' +
							'<td>' + balance_amount.toFixed(2) + '</td>' +
							// '<td><a class="add-jv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
							'</tr>';
						$("table").append(row);
						$("table tbody tr").eq(index + 1).find(".add-jv, .edit-jv").toggle();
						$('[data-toggle="tooltip"]').tooltip();
						parent_amount = parent_amount - parseFloat(b_amount)
					}
				}
			})
	});

	// $('#new-jv-form-crv').on('submit',function(e){
	// 		e.preventDefault();
	// 		var account_id = 0
	// 		var table = $('#new-crv-table');
	// 		var data = [];
	// 		var debit = 0;
	// 		var credit = 0;
	// 		var invoice_no = $('#invoice_no').val();
	// 		var doc_date = $('#doc_date').val();
	// 		var date = $('#date').val();
	// 		var customer = $('#account_title').find(":selected").text();
	// 		var description = $('#description').val();

	// 		table.find('tr').each(function (i, el){
	// 			if(i != 0)
	// 			{
	// 				var $tds = $(this).find('td');
	// 				var row = {
	// 					'account_id' : "",
	// 					'account_title' : "",
	// 					'invoice_no' : "",
	// 					'debit' : "",
	// 					'credit' : "",
	// 					'balance' : "",
	// 				};
	// 				$tds.each(function(i, el){
	// 					if (i === 0) {
	// 							row["account_id"] = ($(this).text());
	// 					}
	// 					if (i === 1) {
	// 							row["account_title"] = ($(this).text());
	// 					}
	// 					else if (i === 2) {
	// 							row["invoice_no"] = ($(this).text());
	// 							debit = debit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 3) {
	// 							row["debit"] = ($(this).text());
	// 							debit = debit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 4) {
	// 							row["credit"] = ($(this).text());
	// 							credit = credit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 5) {
	// 							row["balance"] = ($(this).text());
	// 							credit = credit + parseFloat(($(this).text()));
	// 					}
	// 				});
	// 				data.push(row);
	// 			}
	// 		});

	// 			req =	$.ajax({
	// 				 headers: { "X-CSRFToken": getCookie("csrftoken") },
	// 				 type: 'POST',
	// 				 url : '/transaction/cash_receiving_voucher/new/',
	// 				 data:{
	// 					 'account_id':account_id,
	// 					 'invoice_no': invoice_no,
	// 					 'doc_date': doc_date,
	// 					 'description': description,
	// 					 'date':date,
	// 					 'customer':customer,
	// 					 'items': JSON.stringify(data),
	// 				 },
	// 				 dataType: 'json'
	// 			 })
	// 			 .done(function done(data){
	// 				 alert("CR Voucher Submitted");
	// 				 location.reload();
	// 			 })


	// 	});



	$(".load-invoices-cpv").click(function () {
		var invoice_no = $('#invoice_no').val()
		console.log(invoice_no);
		if ($('#box').prop("checked") == true) {
			var check = 1;
		} else {
			check = 0
		}
		var account_title = $('#account_title').find(":selected").text();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'check': check,
					'invoice_no': invoice_no,
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var balance_amount = 0;
				var parent_amount = $('#amount').val();
				var index = $("table tbody tr:last-child").index();
				for (var i = 0; i < data.pi.length; i++) {
					b_amount = parseFloat(data.pi[i][4]) + parseFloat(data.pi[i][5])
					if (parent_amount > 0) {
						is_abs = parent_amount - parseFloat(b_amount)
						if (parent_amount > parseFloat(b_amount)) {
							balance_amount = 0.00;
						} else {
							parent_amount = parent_amount - parseFloat(b_amount)
							balance_amount = Math.abs(parent_amount)
						}
						var row = '<tr>' +
							'<td>6</td>' +
							'<td>Cash</td>' +
							'<td>' + data.pi[i][2] + '</td>' +
							'<td>0.00</td>' +
							'<td>' + b_amount.toFixed(2) + '</td>' +
							'<td>' + balance_amount.toFixed(2) + '</td>' +
							// '<td><a class="add-jv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-jv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-jv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
							'</tr>';
						$("table").append(row);
						$("table tbody tr").eq(index + 1).find(".add-jv, .edit-jv").toggle();
						$('[data-toggle="tooltip"]').tooltip();
						parent_amount = parent_amount - parseFloat(b_amount)
					}
				}
				$(".load-invoices-cpv").attr("disabled", "disabled");
			})
	});

	// $('#new-jv-form-cpv').on('submit',function(e){
	// 		e.preventDefault();
	// 		var account_id = 0
	// 		var table = $('#new-cpv-table');
	// 		var data = [];
	// 		var debit = 0;
	// 		var credit = 0;
	// 		var invoice_no = $('#invoice_no').val();
	// 		var doc_date = $('#doc_date').val();
	// 		var date = $('#date').val();
	// 		var vendor = $('#account_title').find(":selected").text();
	// 		var description = $('#description').val();
	//
	// 		table.find('tr').each(function (i, el){
	// 			if(i != 0)
	// 			{
	// 				var $tds = $(this).find('td');
	// 				var row = {
	// 					'account_id' : "",
	// 					'account_title' : "",
	// 					'invoice_no' : "",
	// 					'debit' : "",
	// 					'credit' : "",
	// 					'balance' : "",
	// 				};
	// 				$tds.each(function(i, el){
	// 					if (i === 0) {
	// 							row["account_id"] = ($(this).text());
	// 					}
	// 					if (i === 1) {
	// 							row["account_title"] = ($(this).text());
	// 					}
	// 					else if (i === 2) {
	// 							row["invoice_no"] = ($(this).text());
	// 							debit = debit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 3) {
	// 							row["debit"] = ($(this).text());
	// 							debit = debit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 4) {
	// 							row["credit"] = ($(this).text());
	// 							credit = credit + parseFloat(($(this).text()));
	// 					}
	// 					else if (i === 5) {
	// 							row["balance"] = ($(this).text());
	// 							credit = credit + parseFloat(($(this).text()));
	// 					}
	// 				});
	// 				data.push(row);
	// 			}
	// 		});
	//
	// 			req =	$.ajax({
	// 				 headers: { "X-CSRFToken": getCookie("csrftoken") },
	// 				 type: 'POST',
	// 				 url : '/transaction/cash_payment_voucher/new/',
	// 				 data:{
	// 					 'account_id':account_id,
	// 					 'invoice_no': invoice_no,
	// 					 'doc_date': doc_date,
	// 					 'description': description,
	// 					 'date':date,
	// 					 'vendor':vendor,
	// 					 'items': JSON.stringify(data),
	// 				 },
	// 				 dataType: 'json'
	// 			 })
	// 			 .done(function done(data){
	// 				 alert("CP Voucher Submitted");
	// 				 location.reload();
	// 			 })
	// 	});


	// Add row on add button click
	$(document).on("click", ".add-crv", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-crv, .edit-crv").toggle();
			$(".add-item-crv").removeAttr("disabled");
		}
	});


	$(document).on("click", ".edit-crv", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-crv, .edit-crv").toggle();
		$(".add-item-cpv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-crv", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-cpv").removeAttr("disabled");
	});

	$(".add-item-brv").click(function () {
		var account_title = $('#account_title').val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_title': account_title,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + data.account_id + '</td>' +
					'<td>' + data.account_title + '</td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td><input type="text" class="form-control" required value="0.00"></td>' +
					'<td width="100px"><a class="add-brv" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-brv" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a> <a class="delete-brv" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".add-brv, .edit-brv").toggle();
				$('[data-toggle="tooltip"]').tooltip();

			})
	});


	// Add row on add button click
	$(document).on("click", ".add-brv", function () {
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
		input.each(function () {
			if (!$(this).val()) {
				$(this).addClass("error");
				empty = true;
			} else {
				$(this).removeClass("error");
			}
		});
		$(this).parents("tr").find(".error").first().focus();
		if (!empty) {
			input.each(function () {
				$(this).parent("td").html($(this).val());
			});
			$(this).parents("tr").find(".add-brv, .edit-brv").toggle();
			$(".add-item-crv").removeAttr("disabled");
		}
	});


	$(document).on("click", ".edit-brv", function () {
		$(this).parents("tr").find("td:not(:last-child)").each(function (i) {
			if (i === 2) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}
			if (i === 3) {
				$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
			}

		});
		$(this).parents("tr").find(".add-brv, .edit-brv").toggle();
		$(".add-item-cpv").attr("disabled", "disabled");
	});

	// Delete row on delete button click
	$(document).on("click", ".delete-brv", function () {
		var row = $(this).closest('tr');
		var siblings = row.siblings();
		siblings.each(function (index) {
			$(this).children('td').first().text(index + 1);
		});
		$(this).parents("tr").remove();
		$(".add-item-cpv").removeAttr("disabled");
	});



	$('#new-jv-form-brv').on('submit', function (e) {
		e.preventDefault();
		var table = $('#new-brv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var doc_no = $('#doc_no').val();
		var cheque_no = $('#cheque_no').val();
		var cheque_date = $('#cheque_date').val();
		var doc_date = $('#doc_date').val()
		var description = $('#description').val();

		table.find('tr').each(function (i, el) {
			if (i != 0) {
				var $tds = $(this).find('td');
				var row = {
					'account_id': "",
					'account_title': "",
					'debit': "",
					'credit': "",
				};
				$tds.each(function (i, el) {
					if (i === 0) {
						row["account_id"] = ($(this).text());
					}
					if (i === 1) {
						row["account_title"] = ($(this).text());
					} else if (i === 2) {
						row["debit"] = ($(this).text());
						debit = debit + parseFloat(($(this).text()));
					} else if (i === 3) {
						row["credit"] = ($(this).text());
						credit = credit + parseFloat(($(this).text()));
					}
				});
				data.push(row);
			}
		});
		if (debit == credit) {
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					data: {
						'doc_no': doc_no,
						'cheque_no': cheque_no,
						'cheque_date': cheque_date,
						'doc_date': doc_date,
						'description': description,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result != "success") {
						alert(data.result)
					} else {
						alert("Voucher Submitted");
						location.reload();
					}
				})
		} else {
			alert("Debit and Credit sides are not same");
		}

	});
	$('#dataTable tbody').on('click', '.edit_list', function () {
		var currrow = $(this).closest('tr');
		var id = currrow.find('td:eq(1)').text();
		var account_title = currrow.find('td:eq(2)').text();
		var parent_type = currrow.find('td:eq(3)').text();
		var opening_balance = currrow.find('td:eq(4)').text();
		var phone_no = currrow.find('td:eq(5)').text();
		var email_address = currrow.find('td:eq(6)').text();
		var ntn = currrow.find('td:eq(7)').text();
		var stn = currrow.find('td:eq(8)').text();
		var cnic = currrow.find('td:eq(9)').text();
		var address = currrow.find('td:eq(10)').text();
		var remarks = currrow.find('td:eq(11)').text();
		var credit_limit = currrow.find('td:eq(12)').text();
		if (opening_balance > 0) {
			$('#debit_edit').prop("checked", true);
		} else {
			$('#credit_edit').prop("checked", true);
		}
		opening_balance = Math.abs(opening_balance);
		$('#id').val(id);
		if(parent_type === '7'){
			$('#account_type option[value=7]').attr('selected','selected');
		}
		else if(parent_type === '16'){
			val = '16'
			$('#account_type option[value=16]').attr('selected','selected');
		}
		else if(parent_type === '4'){
			val = '4'
			$('#account_type option[value=4]').attr('selected','selected');
		}
		else if(parent_type === '74'){
			val = '74'
			$('#account_type option[value=74]').attr('selected','selected');
		}
		$('#account_title').val(account_title);
		$('#opening_balance').val(opening_balance);
		$('#phone_no').val(phone_no);
		$('#email_address').val(email_address);
		$('#ntn').val(ntn);
		$('#stn').val(stn);
		$('#cnic').val(cnic);
		$('#address').val(address);
		$('#remarks').val(remarks);
		$('#credit_limits').val(credit_limit);
	})

	$(".delete-chart-of-account").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/chart_of_account/delete/${this.id}`);
	})
	$(".delete-job-order").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/job_order/delete/${this.id}`);
	})
	$(".delete_purchase").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/purchase/delete/${this.id}`);
	})
	$(".delete_sale").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/sale/delete/${this.id}`);
	})
	$(".delete-journal-voucher").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/journal_voucher/delete/${this.id}`);
	})
	$(".delete-crv-summary").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/cash_receiving_voucher/delete/${this.id}`);
	})
	$(".delete-cpv-summary").on('click', function () {
		$("#modal_delete_button").attr("href", `/transaction/cash_payment_voucher/delete/${this.id}`);
	})
	$(".delete-ur-summary").on('click', function () {
		$("#modal_delete_button").attr("href", `/roles/delete/${this.id}`);
	})


	$(document).ready(function () {
		$('.sort').DataTable();
	});

	$('#sales_tax_invoice').on('click', function () {
		var win = window.open(`sales-tax-print/${edit_id}`, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})

	$('#commercial_invoice').on('click', function () {
		var win = window.open(`commercial-print/${edit_id}`, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})


	$("#customer").focusout(function () {
		account_name = $(this).val()
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				data: {
					'account_name': account_name,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				if (Math.round(data.debit_amount + data.credit_amount).toFixed(2) > 0) {
					$("#credit_balance").val(Math.round(data.debit_amount + data.credit_amount).toFixed(2));
					$("#credit_balance_hidden").val(Math.round(data.debit_amount + data.credit_amount).toFixed(2));
				} else {
					$("#credit_balance").val(0.00);
					$("#credit_balance_hidden").val(0.00);
				}
			})
	});


	$("#account_cpv").on('change', function () {
		var account_cpv = $('#account_cpv').find(":selected").val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '',
				data: {
					'account_cpv': account_cpv
				},
				dataType: 'json'
			})
			.done(function done(data) {
				$("#new-cpv-table tbody tr").empty();
				if (data.pi.length > 0) {
					count = 1;
					row_count = 0
					var balance_amount = 0;
					var parent_amount = $('#amount').val();
					var index = $("table tbody tr:last-child").index();
					for (var i = 0; i < data.pi.length; i++) {
						discount_amount = (parseFloat(data.pi[i][5]) / 100) * parseFloat(data.pi[i][8]).toFixed(2);
						total_amount = (parseFloat(data.pi[i][5]) - discount_amount).toFixed(2);
						balance_amount = total_amount - Math.abs(parseFloat(data.pi[i][6]))
						var row = '<tr>' +
							'<td>' + count++ + '</td>' +
							'<td><b>' + data.pi[i][3] + '</b></td>' +
							'<td align="right">' + total_amount + '</td>' +
							'<td align="right">' + Math.abs(data.pi[i][6].toFixed(2)) + '</td>' +
							'<td align="right"><input type="text" disabled class="form-control form-control-sm invoice_amount"/></td>' +
							'<td align="right">' + balance_amount.toFixed(2) + '</td>' +
							'<td align="center" ><input class="invoice_checked" type="checkbox" ></td>' +
							'</tr>';
						$("#new-cpv-table").append(row);
					}

				} else {
					var row = '<tr>' +
						'<td align="center" colspan="6" >No Data Found</td>' +
						'</tr>';
					$("#new-cpv-table").append(row);
				}
			})
	});

	var check_paying_amount = 0;
	$("#new-cpv-table").on('change', '.invoice_checked', function () {
		$(this).parents('tr:eq(0)').find('td:eq(4) > input').attr("disabled", false)
		var amount = $(this).parents('tr:eq(0)').find('td:eq(4)').text();
		hide_amount = parseFloat($(this).parents('tr:eq(0)').find('td:eq(2)').text()) - parseFloat($(this).parents('tr:eq(0)').find('td:eq(3)').text());
		if (this.checked) {
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').val(hide_amount)
			$(this).parents('tr:eq(0)').find('td:eq(5)').text("0.00")
		} else {
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').attr("disabled", "disabled")
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').val("")
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(hide_amount)
		}
	})


	$("#on_account").change(function () {
		if (this.checked) {
			$("#new-cpv-table").toggleClass("active");
			$("tr").css('color', 'grey');
			$("#new-cpv-table").find("*").attr("disabled", "disabled");
			$('#new-cpv-table > tbody  > tr').each(function (index, tr) {
				check_action = $(this).find('td:eq(5) > input').is(":checked")
				if (check_action) {
					$(this).find('td:eq(5) > input').prop("checked", false);
					$(this).find('td:eq(4) > input').attr("disabled", "disabled");
				}
			});
			$("#paying_amount").prop('disabled', false);
		} else {
			$("#paying_amount").prop('disabled', true);
			$("tr").css('color', 'black');
			$("#new-cpv-table").toggleClass("active");
			$('#new-cpv-table > tbody  > tr').each(function (index, tr) {
				$(this).find('td:eq(6) > input').attr("disabled", false);
			});
		}
	});

	$("#paying_amount").on('keyup', function () {

	})

	$("#new-cpv-table").on('keyup', '.invoice_amount', function () {
		hide_amount = parseFloat($(this).parents('tr:eq(0)').find('td:eq(2)').text()) - parseFloat($(this).parents('tr:eq(0)').find('td:eq(3)').text());
		var invoice_amount = hide_amount - parseFloat($(this).val());
		if (isNaN(invoice_amount)) {
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(hide_amount);
		} else {
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(invoice_amount);
		}

	})


	$('#new-jv-form-cpv').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		paying_amount_checked = $("#on_account").is(":checked");
		var account_id = 0
		var paying_amount = $("#paying_amount").val();
		var table = $('#new-cpv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var invoice_no = $('#invoice_no').val();
		var doc_date = $('#doc_date').val();
		var date = $('#date').val();
		var vendor = $('#account_cpv').find(":selected").val();
		var description = $('#description').val();

		if (paying_amount_checked) {

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/cash_payment_voucher/new/',
					data: {
						'doc_date': doc_date,
						'description': description,
						'date': date,
						'vendor': vendor,
						'on_account': 1,
						'paying_amount': paying_amount,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result) {
						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/cpv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				});
		} else {
			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'account_id': "",
						'invoice_amount': "",
						'invoice_no': "",
					};
					row_checked = $(el).find('td:eq(6) > input').is(":checked");
					$tds.each(function (i, el) {
						if (row_checked) {
							if (i === 0) {
								row["account_id"] = vendor;
							} else if (i === 1) {
								row["invoice_no"] = $(this).text();
							} else if (i === 4) {
								row["invoice_amount"] = ($(this).find('input').val());
								data.push(row);
							}
						}
					});
				}
			});
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/cash_payment_voucher/new/',
					data: {
						'doc_date': doc_date,
						'description': description,
						'date': date,
						'vendor': vendor,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {

					if (data.result) {
						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/cpv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				});
		}
	});


	// =============================================================================


	$("#account_crv").on('change', function () {
		var account_crv = $('#account_crv').find(":selected").val();
		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '',
				data: {
					'account_crv': account_crv
				},
				dataType: 'json'
			})
			.done(function done(data) {
				console.log(data);
				$("#new-crv-table tbody tr").empty();
				if (data.pi.length > 0) {
					count = 1;
					row_count = 0
					var balance_amount = 0;
					var parent_amount = $('#amount').val();
					var index = $("table tbody tr:last-child").index();
					for (var i = 0; i < data.pi.length; i++) {
						gst = (parseFloat(data.pi[i][5]) * parseFloat(data.pi[i][8]) / 100)
						srb = (parseFloat(data.pi[i][5]) * parseFloat(data.pi[i][9]) / 100)
						total_amount_before_discount = parseFloat(data.pi[i][5].toFixed(2)) + parseFloat(gst) + parseFloat(srb)
						discount_amount = (total_amount_before_discount / 100) * parseFloat(data.pi[i][10]).toFixed(2)
						total_amount = total_amount_before_discount - discount_amount
						balance_amount = total_amount - Math.abs(parseFloat(data.pi[i][6]))
						var row = '<tr>' +
							'<td>' + count++ + '</td>' +
							'<td><b>' + data.pi[i][3] + '</b></td>' +
							'<td align="right">' + total_amount.toFixed(2) + '</td>' +
							'<td align="right">' + Math.abs(data.pi[i][6].toFixed(2)) + '</td>' +
							'<td align="right"><input type="text" disabled class="form-control form-control-sm invoice_amount"/></td>' +
							'<td align="right">' + balance_amount.toFixed(2) + '</td>' +
							'<td align="center" ><input class="invoice_checked" type="checkbox" ></td>' +
							'</tr>';
						$("#new-crv-table").append(row);
					}

				} else {
					var row = '<tr>' +
						'<td align="center" colspan="6" >No Data Found</td>' +
						'</tr>';
					$("#new-crv-table").append(row);
				}
			})
	});

	var check_paying_amount = 0;
	$("#new-crv-table").on('change', '.invoice_checked', function () {
		$(this).parents('tr:eq(0)').find('td:eq(4) > input').attr("disabled", false)
		var amount = $(this).parents('tr:eq(0)').find('td:eq(4)').text();
		hide_amount = parseFloat($(this).parents('tr:eq(0)').find('td:eq(2)').text()) - parseFloat($(this).parents('tr:eq(0)').find('td:eq(3)').text());
		if (this.checked) {
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').val(hide_amount)
			$(this).parents('tr:eq(0)').find('td:eq(5)').text("0.00")
		} else {
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').attr("disabled", "disabled")
			$(this).parents('tr:eq(0)').find('td:eq(4) > input').val("")
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(hide_amount)
		}
	})


	$("#on_account_crv").change(function () {
		if (this.checked) {
			$("#new-crv-table").toggleClass("active");
			$("tr").css('color', 'grey');
			$("#new-crv-table").find("*").attr("disabled", "disabled");
			$('#new-crv-table > tbody  > tr').each(function (index, tr) {
				check_action = $(this).find('td:eq(5) > input').is(":checked")
				if (check_action) {
					$(this).find('td:eq(5) > input').prop("checked", false);
					$(this).find('td:eq(4) > input').attr("disabled", "disabled");
				}
			});
			$("#receiving_amount").prop('disabled', false);
		} else {
			$("#receiving_amount").prop('disabled', true);
			$("tr").css('color', 'black');
			$("#new-crv-table").toggleClass("active");
			$('#new-crv-table > tbody  > tr').each(function (index, tr) {
				$(this).find('td:eq(6) > input').attr("disabled", false);
			});
		}
	});

	$("#receiving_amount").on('keyup', function () {

	})

	$("#new-crv-table").on('keyup', '.invoice_amount', function () {
		hide_amount = parseFloat($(this).parents('tr:eq(0)').find('td:eq(2)').text()) - parseFloat($(this).parents('tr:eq(0)').find('td:eq(3)').text());
		var invoice_amount = hide_amount - parseFloat($(this).val());
		if (isNaN(invoice_amount)) {
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(hide_amount);
		} else {
			$(this).parents('tr:eq(0)').find('td:eq(5)').text(invoice_amount);
		}

	})


	$('#new-jv-form-crv').on('submit', function (e) {
		e.preventDefault();
		$(".disable_on_submit").prop('disabled', true);
		receiving_amount_checked = $("#on_account_crv").is(":checked");
		var account_id = 0
		var receiving_amount = $("#receiving_amount").val();
		var table = $('#new-crv-table');
		var data = [];
		var debit = 0;
		var credit = 0;
		var invoice_no = $('#invoice_no').val();
		var doc_date = $('#doc_date').val();
		var date = $('#date').val();
		var vendor = $('#account_crv').find(":selected").val();
		var description = $('#description').val();
		if (receiving_amount_checked) {
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/cash_receiving_voucher/new/',
					data: {
						'doc_date': doc_date,
						'description': description,
						'date': date,
						'vendor': vendor,
						'on_account_crv': 1,
						'receiving_amount': receiving_amount,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result) {
						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/crv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				});
		} else {
			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'account_id': "",
						'invoice_amount': "",
						'invoice_no': "",
					};
					row_checked = $(el).find('td:eq(6) > input').is(":checked");
					$tds.each(function (i, el) {
						if (row_checked) {
							if (i === 0) {
								row["account_id"] = vendor;
							} else if (i === 1) {
								row["invoice_no"] = $(this).text();
							} else if (i === 4) {
								row["invoice_amount"] = ($(this).find('input').val());
								data.push(row);
							}
						}
					});
				}
			});
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/cash_receiving_voucher/new/',
					data: {
						'doc_date': doc_date,
						'description': description,
						'date': date,
						'vendor': vendor,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done(data) {
					if (data.result) {
						$.toast().reset('all');
						$.toast({
							heading: 'Submitted Successfully',
							text: 'Yes! check here <a href="/transaction/crv_pdf/' + data.header_id + '" target="_blank">' + data.doc_no + '</a>.',
							hideAfter: false,
							icon: 'success',
							'position': 'mid-center'
						})
						setInterval(function () {
							location.reload()
						}, 2000);
					} else {
						$(".disable_on_submit").prop('disabled', false);
						var myToast = $.toast({
							text: data.e,
							hideAfter: false,
							bgColor: '#E01A31',
							'position': 'bottom-left',
							icon: 'error'
						});
					}
				});
		}
	});

	// // Chart of account tree view click
	// $('.tree_account').on('click', function () {
	// 	req = $.ajax({
	// 			headers: {
	// 				"X-CSRFToken": getCookie("csrftoken")
	// 			},
	// 			type: 'POST',
	// 			url: '/transaction/chart_of_account/',
	// 			data: {
	// 				'tree_id': $(this).data("id")
	// 			},
	// 			dataType: 'json'
	// 		})
	// 		.done(function done(data) {
	// 			for (let index = 0; index < data.child_list.length; index++) {

	// 				var table = 
	// 					'<tr>' +
	// 					'<td>{{ forloop.counter }}</td>' +
	// 					'<td style="display:none;">{{ value.id }}</td>' +
	// 					'<td>'+data.child_list[index].account_title+'</td>' +
	// 					'<td style="display:none;">{{ value.parent_id }}</td>' +
	// 					'<td style="display:;">{{ value.opening_balance }}</td>' +
	// 					'<td style="display:;">{{ value.phone_no }}</td>' +
	// 					'<td style="display:;">{{ value.email_address }}</td>' +
	// 					'<td style="display:;">{{ value.ntn }}</td>' +
	// 					'<td style="display:;">{{ value.stn }}</td>' +
	// 					'<td style="display:none;">{{ value.cnic }}</td>' +
	// 					'<td style="display:none;">{{ value.Address }}</td>' +
	// 					'<td style="display:none;">{{ value.remarks }}</td>' +
	// 					'<td style="display:none;">{{ value.credit_limit }}</td>' +
	// 					'<td>' +
	// 					'<a class="edit_list has_id" href="#" data-toggle="modal" data-target="#editCoaModal" id="{{value.id}}">' +
	// 					'<i class="material-icons">&#xE254;</i></a>' +
	// 					//   '<a class="edit_list disableClick"><i class="material-icons">&#xE254;</i></a>'+
	// 					'<a class="delete-chart-of-account" href="#" data-toggle="modal" data-target="#deleteCoaModal"' +
	// 					'id="{{value.id}}"><i class="material-icons">&#xE872;</i></a>' +
	// 					//   '<a class="delete-chart-of-account disableClick"><i class="material-icons">&#xE872;</i></a>'+
	// 					'</td>' +
	// 					'</tr>'
	// 					console.log($("#coa_div table tbody"));

	// 				$("#coa_div table tbody").append(table);
	// 			}
	// 		});

	// })

	// Sale Return 

	$('#sale-return-submit').on('submit', function (e) {
		e.preventDefault();
		form_id = $("#form_id").val();
		if (form_id === "0") {
			var table = $('#sale-return-table');
			var data = [];
			var sale_id = $('#sale_id').val();
			var customer = $('#customer').val();
			var account_holder = $('#account_holder').val();
			var payment_method = $('#payment_method').val();
			var footer_desc = $('#footer_desc').val();
			var discount = $('#discount').val();
			var date = $('#date').val();

			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'item_id': "",
						'description': "",
						'width': "",
						'height': "",
						'quantity': "",
						'sqft': "",
						'rate': "",
						'total': "",
						'measurment': "",
					};
					$tds.each(function (i, el) {
						if (i === 1) {
							row["item_id"] = ($(this).text());
						}
						if (i === 4) {
							row["description"] = ($(this).find('input').val());
						} else if (i === 6) {
							row["width"] = ($(this).text());
						} else if (i === 7) {
							row["height"] = ($(this).text());
						} else if (i === 8) {
							is_und = ($(this).find('input').val())
							if (typeof is_und == "undefined") {
								row["quantity"] = ($(this).text());
							} else {
								row["quantity"] = ($(this).find('input').val());
							}
						} else if (i === 9) {
							row["sqft"] = ($(this).text());
						} else if (i === 10) {
							row["rate"] = ($(this).find('input').val());
						} else if (i === 11) {
							row["total"] = ($(this).text());
						} else if (i === 12) {
							row["measurment"] = ($(this).text());
						}
					});
					data.push(row);
				}
			});

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale_return/new',
					data: {
						'sale_id': sale_id,
						'customer': customer,
						'account_holder': account_holder,
						'payment_method': payment_method,
						'footer_desc': footer_desc,
						"discount": discount,
						'date': date,
						'form_id': form_id,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done() {
					alert("Sales Created");
					location.reload();
				})
		} else {
			var table = $('#sale-return-table');
			var data = [];
			var sale_id = $('#sale_id').val();
			var customer = $('#customer').val();
			var account_holder = $('#account_holder').val();
			var payment_method = $('#payment_method').val();
			var footer_desc = $('#footer_desc').val();
			var discount = $('#discount').val();
			var date = $('#date').val();

			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'item_id': "",
						'description': "",
						'width': "",
						'height': "",
						'quantity': "",
						'sqft': "",
						'rate': "",
						'total': "",
						'measurment': "",
					};
					$tds.each(function (i, el) {
						if (i === 1) {
							row["item_id"] = ($(this).text());
						}
						if (i === 4) {
							row["description"] = ($(this).find('input').val());
						} else if (i === 6) {
							row["width"] = ($(this).text());
						} else if (i === 7) {
							row["height"] = ($(this).text());
						} else if (i === 8) {
							is_und = ($(this).find('input').val())
							if (typeof is_und == "undefined") {
								row["quantity"] = ($(this).text());
							} else {
								row["quantity"] = ($(this).find('input').val());
							}
						} else if (i === 9) {
							row["sqft"] = ($(this).text());
						} else if (i === 10) {
							row["rate"] = ($(this).find('input').val());
						} else if (i === 11) {
							row["total"] = ($(this).text());
						} else if (i === 12) {
							row["measurment"] = ($(this).text());
						}
					});
					data.push(row);
				}
			});

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale_return/new',
					data: {
						'sale_id': sale_id,
						'customer': customer,
						'account_holder': account_holder,
						'payment_method': payment_method,
						'footer_desc': footer_desc,
						"discount": discount,
						'date': date,
						'form_id': form_id,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done() {
					alert("Sale Return Updated");
					location.reload();
				})
		}
	});

	// ADDING IN SALE RETURN ITEMS

	$(".add-item-sale-return").click(function () {
		var job_no_sale = "";
		var job_no_sale = $('#job_no_sale_return').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/sale_return/new',
				data: {
					'job_no_sale': job_no_sale,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				for (var i = 0; i < data.items.length; i++) {
					if (data.items[i][3] == "sq.ft") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit * parseFloat(data.items[i][6])
					} else if (data.items[i][3] == "sq.inches") {
						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
						square_fit = square_fit / 144
						square_fit = square_fit * parseFloat(data.items[i][6])
					}
					var index = $("table tbody tr:last-child").index();
					// console.log(data.items[i][7]);

					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td style="display:none;">' + data.items[i][7] + '</td>' +
						'<td>' + data.items[i][0] + '</td>' +
						'<td>' + data.items[i][1] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control"></td>' +
						'<td>' + data.items[i][3] + '</td>' +
						'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
						'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
						'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
						'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;">' + data.items[i][3] + '</td>' +
						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$('#item_code_sale').val("");
				}
			});
	});


	$('#job_no_sale_return').on('keypress', function (e) {
		if (e.which == 13) {
			e.preventDefault();
			var job_no_sale = "";
			var job_no_sale = $('#job_no_sale_return').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale_return/new',
					data: {
						'job_no_sale': job_no_sale,
					},
					dataType: 'json'
				})
				.done(function done(data) {

					for (var i = 0; i < data.items.length; i++) {
						if (data.items[i][3] == "sq.ft") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit * parseFloat(data.items[i][6])
						} else if (data.items[i][3] == "sq.inches") {
							square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
							square_fit = square_fit / 144
							square_fit = square_fit * parseFloat(data.items[i][6])
						}
						var index = $("table tbody tr:last-child").index();
						var row = '<tr>' +
							'<td>' + count + '</td>' +
							'<td style="display:none;">' + data.items[i][7] + '</td>' +
							'<td>' + data.items[i][0] + '</td>' +
							'<td>' + data.items[i][1] + '</td>' +
							'<td><input type="text" style="width:300px;" class="form-control" value=" "></td>' +
							'<td>' + data.items[i][3] + '</td>' +
							'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
							'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
							'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
							'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
							'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
							'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
							'<td style="display:none;">' + data.items[i][3] + '</td>' +
							'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
							'</tr>';
						count++;
						$("table").append(row);
						$('#item_code_sale').val("");
					}
				});
		}
	});

	$(".add-item-x-return").click(function () {
		var x_stand = $('#x_stand_return').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/sale_return/new',
				data: {
					'x_stand': x_stand,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items);
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td style="display:none;">' + type[0].pk + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><input type="text" style="width:300px;" class="form-control"></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0</td>' +
					'<td id="height">0</td>' +
					'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_sale"></td>' +
					'<td id="sqft">0</td>' +
					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_sale"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;"></td>' +
					'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$('#item_code_sale').val("");
			});
	});

	$('#x_stand_return').on('keypress', function (e) {
		if (e.which == 13) {
			e.preventDefault();
			var x_stand = $('#x_stand_return').val();

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/sale_return/new',
					data: {
						'x_stand': x_stand,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td style="display:none;">' + type[0].pk + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control"></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0</td>' +
						'<td id="height">0</td>' +
						'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_sale"></td>' +
						'<td id="sqft">0</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_sale"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;"></td>' +
						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-sale, .add-transaction-sale").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");

				});
		}
	});


	var sum = 0;
	$('#sale-return-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(11)');
		var total = tdObject.text()
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}

		var discount = $("#discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val").val();
		var amount_before_discount = parseFloat(sum);

		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		} else {
			discount_amount = 0;
		}
		$('#grand_total').val((sum - discount_in_val).toFixed(2));
	});


	// PURCHASE RETURN


	$('#purchase-return-submit').on('submit', function (e) {
		e.preventDefault();
		form_id = $("#form_id").val();
		if (form_id === "0") {
			var table = $('#purchase-return-table');
			var data = [];
			var sale_id = $('#purchase_id').val();
			var vendor = $('#vendor').val();
			var account_holder = $('#account_holder').val();
			var payment_method = $('#payment_method').val();
			var footer_desc = $('#footer_desc').val();
			var discount = $('#discount').val();
			var date = $('#date').val();

			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'item_id': "",
						'description': "",
						'width': "",
						'height': "",
						'quantity': "",
						'sqft': "",
						'rate': "",
						'total': "",
						'measurment': "",
					};
					$tds.each(function (i, el) {
						if (i === 1) {
							row["item_id"] = ($(this).text());
						}
						if (i === 4) {
							row["description"] = ($(this).find('input').val());
						} else if (i === 6) {
							row["width"] = ($(this).text());
						} else if (i === 7) {
							row["height"] = ($(this).text());
						} else if (i === 8) {
							is_und = ($(this).find('input').val())
							if (typeof is_und == "undefined") {
								row["quantity"] = ($(this).text());
							} else {
								row["quantity"] = ($(this).find('input').val());
							}
						} else if (i === 9) {
							row["sqft"] = ($(this).text());
						} else if (i === 10) {
							row["rate"] = ($(this).find('input').val());
						} else if (i === 11) {
							row["total"] = ($(this).text());
						} else if (i === 12) {
							row["measurment"] = ($(this).text());
						}
					});
					data.push(row);
				}
			});

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase_return/new',
					data: {
						'purchase_id': purchase_id,
						'vendor': vendor,
						'account_holder': account_holder,
						'payment_method': payment_method,
						'footer_desc': footer_desc,
						"discount": discount,
						'date': date,
						'form_id': form_id,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done() {
					alert("Purchase Created");
					location.reload();
				})
		} else {
			var table = $('#purchase-return-table');
			var data = [];
			var sale_id = $('#purchase_id').val();
			var vendor = $('#vendor').val();
			var account_holder = $('#account_holder').val();
			var payment_method = $('#payment_method').val();
			var footer_desc = $('#footer_desc').val();
			var discount = $('#discount').val();
			var date = $('#date').val();

			table.find('tr').each(function (i, el) {
				if (i != 0) {
					var $tds = $(this).find('td');
					var row = {
						'item_id': "",
						'description': "",
						'width': "",
						'height': "",
						'quantity': "",
						'sqft': "",
						'rate': "",
						'total': "",
						'measurment': "",
					};
					$tds.each(function (i, el) {
						if (i === 1) {
							row["item_id"] = ($(this).text());
						}
						if (i === 4) {
							row["description"] = ($(this).find('input').val());
						} else if (i === 6) {
							row["width"] = ($(this).text());
						} else if (i === 7) {
							row["height"] = ($(this).text());
						} else if (i === 8) {
							is_und = ($(this).find('input').val())
							if (typeof is_und == "undefined") {
								row["quantity"] = ($(this).text());
							} else {
								row["quantity"] = ($(this).find('input').val());
							}
						} else if (i === 9) {
							row["sqft"] = ($(this).text());
						} else if (i === 10) {
							row["rate"] = ($(this).find('input').val());
						} else if (i === 11) {
							row["total"] = ($(this).text());
						} else if (i === 12) {
							row["measurment"] = ($(this).text());
						}
					});
					data.push(row);
				}
			});

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase_return/new',
					data: {
						'purchase_id': spurchase_id,
						'vendor': vendor,
						'account_holder': account_holder,
						'payment_method': payment_method,
						'footer_desc': footer_desc,
						"discount": discount,
						'date': date,
						'form_id': form_id,
						'items': JSON.stringify(data),
					},
					dataType: 'json'
				})
				.done(function done() {
					alert("Purchase Return Updated");
					location.reload();
				})
		}
	});

	// ADDING IN PURCHASE RETURN ITEMS

	// $(".add-item-purchase-return").click(function () {
	// 	var job_no_sale = "";
	// 	var job_no_sale = $('#job_no_sale_return').val();

	// 	req = $.ajax({
	// 			headers: {
	// 				"X-CSRFToken": getCookie("csrftoken")
	// 			},
	// 			type: 'POST',
	// 			url: '/transaction/sale_return/new',
	// 			data: {
	// 				'job_no_sale': job_no_sale,
	// 			},
	// 			dataType: 'json'
	// 		})
	// 		.done(function done(data) {
	// 			for (var i = 0; i < data.items.length; i++) {
	// 				if (data.items[i][3] == "sq.ft") {
	// 					square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
	// 					square_fit = square_fit * parseFloat(data.items[i][6])
	// 				} else if (data.items[i][3] == "sq.inches") {
	// 					square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
	// 					square_fit = square_fit / 144
	// 					square_fit = square_fit * parseFloat(data.items[i][6])
	// 				}
	// 				var index = $("table tbody tr:last-child").index();
	// 				// console.log(data.items[i][7]);

	// 				var row = '<tr>' +
	// 					'<td>' + count + '</td>' +
	// 					'<td style="display:none;">' + data.items[i][7] + '</td>' +
	// 					'<td>' + data.items[i][0] + '</td>' +
	// 					'<td>' + data.items[i][1] + '</td>' +
	// 					'<td><input type="text" style="width:300px;" class="form-control"></td>' +
	// 					'<td>' + data.items[i][3] + '</td>' +
	// 					'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
	// 					'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
	// 					'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
	// 					'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
	// 					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
	// 					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
	// 					'<td style="display:none;">' + data.items[i][3] + '</td>' +
	// 					'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
	// 					'</tr>';
	// 				count++;
	// 				$("table").append(row);
	// 				$('#item_code_sale').val("");
	// 			}
	// 		});
	// });


	// $('#job_no_sale_return').on('keypress', function (e) {
	// 	if (e.which == 13) {
	// 		e.preventDefault();
	// 		var job_no_sale = "";
	// 		var job_no_sale = $('#job_no_sale_return').val();
	// 		req = $.ajax({
	// 				headers: {
	// 					"X-CSRFToken": getCookie("csrftoken")
	// 				},
	// 				type: 'POST',
	// 				url: '/transaction/sale_return/new',
	// 				data: {
	// 					'job_no_sale': job_no_sale,
	// 				},
	// 				dataType: 'json'
	// 			})
	// 			.done(function done(data) {

	// 				for (var i = 0; i < data.items.length; i++) {
	// 					if (data.items[i][3] == "sq.ft") {
	// 						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
	// 						square_fit = square_fit * parseFloat(data.items[i][6])
	// 					} else if (data.items[i][3] == "sq.inches") {
	// 						square_fit = parseFloat(data.items[i][4]) * parseFloat(data.items[i][5])
	// 						square_fit = square_fit / 144
	// 						square_fit = square_fit * parseFloat(data.items[i][6])
	// 					}
	// 					var index = $("table tbody tr:last-child").index();
	// 					var row = '<tr>' +
	// 						'<td>' + count + '</td>' +
	// 						'<td style="display:none;">' + data.items[i][7] + '</td>' +
	// 						'<td>' + data.items[i][0] + '</td>' +
	// 						'<td>' + data.items[i][1] + '</td>' +
	// 						'<td><input type="text" style="width:300px;" class="form-control" value=" "></td>' +
	// 						'<td>' + data.items[i][3] + '</td>' +
	// 						'<td id="width">' + data.items[i][4].toFixed(2) + '</td>' +
	// 						'<td id="height">' + data.items[i][5].toFixed(2) + '</td>' +
	// 						'<td id="quantity">' + data.items[i][6].toFixed(2) + '</td>' +
	// 						'<td id="sqft">' + square_fit.toFixed(2) + '</td>' +
	// 						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_rate_sale"></td>' +
	// 						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
	// 						'<td style="display:none;">' + data.items[i][3] + '</td>' +
	// 						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
	// 						'</tr>';
	// 					count++;
	// 					$("table").append(row);
	// 					$('#item_code_sale').val("");
	// 				}
	// 			});
	// 	}
	// });

	$(".add-item-x-return-purchase").click(function () {
		var x_stand = $('#x_stand_return').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/purchase_return/new',
				data: {
					'x_stand': x_stand,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items);
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td style="display:none;">' + type[0].pk + '</td>' +
					'<td>' + type[0].fields["item_code"] + '</td>' +
					'<td>' + type[0].fields["item_name"] + '</td>' +
					'<td><input type="text" style="width:300px;" class="form-control"></td>' +
					'<td>' + type[0].fields["unit"] + '</td>' +
					'<td id="width">0</td>' +
					'<td id="height">0</td>' +
					'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_purchase"></td>' +
					'<td id="sqft">0</td>' +
					'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_purchase"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;"></td>' +
					'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$('#item_code_purchase').val("");
			});
	});

	$('#x_stand_return_purchase').on('keypress', function (e) {
		if (e.which == 13) {
			e.preventDefault();
			var x_stand = $('#x_stand_return_purchase').val();

			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase_return/new',
					data: {
						'x_stand': x_stand,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)
					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td style="display:none;">' + type[0].pk + '</td>' +
						'<td>' + type[0].fields["item_code"] + '</td>' +
						'<td>' + type[0].fields["item_name"] + '</td>' +
						'<td><input type="text" style="width:300px;" class="form-control"></td>' +
						'<td>' + type[0].fields["unit"] + '</td>' +
						'<td id="width">0</td>' +
						'<td id="height">0</td>' +
						'<td id="quantity"><input type="text" style="width:80px;" class="form-control input_x_quantity_purchase"></td>' +
						'<td id="sqft">0</td>' +
						'<td id="rate"><input type="text" style="width:80px;" class="form-control input_x_rate_purchase"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;"></td>' +
						'<td><a class="delete-transaction-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-sale, .add-transaction-sale").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_purchase').val("");

				});
		}
	});


	var sum = 0;
	$('#purchase-return-table tbody tr').each(function () {
		var tdObject = $(this).find('td:eq(11)');
		var total = tdObject.text()
		if (!isNaN(total) && total.length !== 0) {
			sum += parseFloat(total);
		}

		var discount = $("#discount").val();
		var discount_amount = 0
		var discount_in_val = $("#discount_in_val").val();
		var amount_before_discount = parseFloat(sum);

		if (discount_in_val != 0) {
			discount_amount = (amount_before_discount / 100) * discount_in_val;
		} else {
			discount_amount = 0;
		}
		$('#grand_total').val((sum - discount_in_val).toFixed(2));
	});

	$("#item_no_purchase_return").keypress(function (e) {
		e.preventDefault();
		if (e.which == 13) {
			var item_code_purchase = $('#item_no_purchase_return').val();
			req = $.ajax({
					headers: {
						"X-CSRFToken": getCookie("csrftoken")
					},
					type: 'POST',
					url: '/transaction/purchase_return/new',
					data: {
						'item_code_purchase': item_code_purchase,
					},
					dataType: 'json'
				})
				.done(function done(data) {
					type = JSON.parse(data.items)

					var index = $("table tbody tr:last-child").index();
					var row = '<tr>' +
						'<td>' + count + '</td>' +
						'<td>' + type[0].fields['item_code'] + '</td>' +
						'<td>' + type[0].fields['item_name'] + '</td>' +
						'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
						'<td ><select id="sel" class="form-control input_select" style="height:40px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
						'<td id="width"><input type="text" required class="form-control input_width"></td>' +
						'<td id="height"><input type="text" required class="form-control input_height"></td>' +
						'<td id="quantity"><input type="text" required class="form-control input_quantity"></td>' +
						'<td id="square_fit"></td>' +
						'<td id="rate" ><input type="text" style="width:70px;" required class="form-control input_rate"></td>' +
						'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
						'<td style="display:none;" id="measurment">sq.ft</td>' +
						'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
						'</tr>';
					count++;
					$("table").append(row);
					$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
					$('[data-toggle="tooltip"]').tooltip();
					$('#item_code_sale').val("");
				});
		}
	})

	$(".add-item-purchase-return").click(function () {
		var item_code_purchase = $('#item_no_purchase_return').val();

		req = $.ajax({
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				type: 'POST',
				url: '/transaction/purchase_return/new',
				data: {
					'item_code_purchase': item_code_purchase,
				},
				dataType: 'json'
			})
			.done(function done(data) {
				type = JSON.parse(data.items)
				var index = $("table tbody tr:last-child").index();
				var row = '<tr>' +
					'<td>' + count + '</td>' +
					'<td>' + type[0].fields['item_code'] + '</td>' +
					'<td>' + type[0].fields['item_name'] + '</td>' +
					'<td><pre>' + type[0].fields['item_description'] + '</pre></td>' +
					'<td ><select id="sel" class="form-control input_select" style="height:40px;"><option>sq.ft</option><option>sq.inches</option></select></td>' +
					'<td id="width"><input type="text" required class="form-control input_width"></td>' +
					'<td id="height"><input type="text" required class="form-control input_height"></td>' +
					'<td id="quantity"><input type="text" required class="form-control input_quantity"></td>' +
					'<td id="square_fit"></td>' +
					'<td id="rate" ><input type="text" style="width:70px;" required class="form-control input_rate"></td>' +
					'<td id="total" style="font-weight:bold;" class="sum"><b>0.00</b></td>' +
					'<td style="display:none;" id="measurment">sq.ft</td>' +
					'<td><a class="edit-transaction-purchase" title="Edit" data-toggle="tooltip" id="edit_purchase"><i class="material-icons">&#xE254;</i></a><a class="delete-transaction-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
					'</tr>';
				count++;
				$("table").append(row);
				$("table tbody tr").eq(index + 1).find(".edit-transaction-purchase, .add-transaction-purchase").toggle();
				$('[data-toggle="tooltip"]').tooltip();
				$('#item_code_sale').val("");
			});
	});

	$("#generate_trial_balance").on('click', function () {
		from_date = $("#from_date_trial_balance").val()
		to_date = $("#to_date_trial_balance").val()
		url = `/transaction/trial_balance/pdf/${from_date}/${to_date}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})

	$("#generate_account_ledger").on('click', function () {
		from_date = $("#from_date_ledger").val()
		to_date = $("#to_date_ledger").val()
		var ledger_account = $('#ledger_account').find(":selected").val();
		url = `/transaction/account_ledger/pdf/${ledger_account}/${from_date}/${to_date}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})


	$("#generate_receivable_ledger").on('click', function () {
		var ledger_account = $('#r_ledger').find(":selected").val();
		url = `/transaction/receivable_ledger/pdf/${ledger_account}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})


	$("#generate_payable_ledger").on('click', function () {
		var ledger_account = $('#p_ledger').find(":selected").val();
		url = `/transaction/payable_ledger/pdf/${ledger_account}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})


	$("#generate_sale_detail").on('click', function () {
		from_date = $("#from_date_s_d").val()
		to_date = $("#to_date_s_d").val()
		url = `/transaction/sale_detail_report/pdf/${from_date}/${to_date}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})


	$("#generate_daily_report").on('click', function () {
		from_date = $("#from_date_d_r").val()
		to_date = $("#to_date_d_r").val()
		url = `/transaction/daily_report/pdf/${from_date}/${to_date}`
		var win = window.open(url, '_blank');
		if (win) {
			//Browser has allowed it to be opened
			win.focus();
		} else {
			//Browser has blocked it
			alert('Please allow popups for this website');
		}
	})

	$("#generate_sales_taxt_reports").on('click', function () {
		from_date = $("#from_date_st_r").val()
		to_date = $("#to_date_st_r").val()
		req = $.ajax({
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			},
			type: 'POST',
			url: 'reports_all_sales_tax_inv/',
			data: {
				'from_date': from_date,
				'to_date':to_date,
			},
			dataType: 'json'
		})
		.done(function(data){
		if (data.inv.length <= 0) {
			$.toast({
				heading: 'No GST and SRB invoice found!',
				hideAfter: true,
				icon: 'warning',
				'position': 'bottom-left'
			})		
		} else {
			for (let i = 0; i < data.inv.length; i++) {
				url = `report_sales_tax_print/${data.inv[i]}`		
				var win = window.open(url, '_blank');
				if (win) {
					//Browser has allowed it to be opened
					win.focus();
				} else {
					//Browser has blocked it
					alert('Please allow popups for this website');
				}
			}
		}			
		})
	})

});