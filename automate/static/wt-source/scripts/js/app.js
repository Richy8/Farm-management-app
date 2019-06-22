(function ($) {

	/*Animate Effect
	===============*/
	new WOW().init({
		mobile: true
	});

	/*Profile Dropdown
	==================*/
	let target = $('.profile-info .user-name');
	let dropDown = $('.profile-info .more');

	$(target).on('click', function () {
		// console.log('click');
		$(dropDown).toggleClass('show');
	})

	let caret = $('.right-head .profile-name .fas')
	let dropDown2 = $('.right-head .profile-name .dropdownMenu')
	let drop = $('.right-head .profile-name::after')

	$(caret).on('click', function () {
		// console.log('click');
		$(dropDown2).toggleClass('show');
		$(drop).toggleClass('show');
	})


	/*Ellipsis Dropdown
	====================*/
	let ellipsis = $('#ellipsis');
	let righthead = $('.header-div .col-md-10');

	$(ellipsis).on('click', function () {
		// console.log('click');
		$(righthead).toggleClass('show');
	})

	/*Side-bar PullOut
	==================*/
	let menuBar = $('#bars'); 
	let sideBar = $('.sidebar-div .col-md-2');

	$(menuBar).on('click', function(){
		$(sideBar).toggleClass('show');
	})

	/*NOTIFICATIONS DROPDOWN
	==================*/
	let notification_icon = $('#dropDown');
	let notification_dropdown = $('#dropMenu');
	
	$(notification_icon).on('click', function(){
		$(notification_dropdown).toggleClass('show');
	})
	

})(jQuery);