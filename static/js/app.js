var app = angular.module('app', [])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');
	});

app.controller("RoomController", function(){
    this.title = 'AngularJS Works!';
});

app.controller('RoomAPIController', ['$http',function($http){
	var value = this;
	value.title = [];
	$http.get('/api/rooms/room_1/').success(function(data){
		value.data = data;
	});
}]);