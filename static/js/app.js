var app = angular.module('app', ['ngRoute'])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');

	})
	.config(['$routeProvider', function($routeProvider) {
	    $routeProvider.when('/rooms/:roomName', {
	        controller: 'RoomController',
	        controllerAs: 'room',
	        templateUrl: 'static/detail.html'
	    })
	    .when('/sup', {
	        controller: 'RoomAPIController',
	        template: '<strong></strong>'
	    });
	}])
    .controller('RoomController',['$http', '$routeParams', function($http, $routeParams){
        console.log($routeParams);
        var value = this;
        value.title = [];
        $http.get('/api/rooms/' + $routeParams.roomName).success(function(data){
            value.title=data;
            value.data = data;
        });
    }]);
