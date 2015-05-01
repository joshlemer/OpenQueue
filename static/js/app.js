var app = angular.module('app', ['ngRoute', 'mgcrea.ngStrap'])//ui.bootstrap' ])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');

	})
	.config(['$routeProvider', function($routeProvider) {
	    $routeProvider
	    .when('/', {
	        controller: 'RoomListController',
	        controllerAs: 'list',
	        templateUrl: 'static/list.html'
	    })
	    .when('/rooms/:roomName', {
	        controller: 'RoomController',
	        controllerAs: 'room',
	        templateUrl: 'static/detail.html'
	    })
	    .when('/sup', {
	        controller: 'RoomAPIController',
	        template: '<strong></strong>'
	    });
	}])
    .controller('RoomController',['$http', '$routeParams','$scope', function($http, $routeParams, $scope){
        console.log($routeParams);
        var value = this;
        value.title = [];
        $http.get('/api/rooms/' + $routeParams.roomName).success(function(data){
            value.title=data;
            value.data = data;
            $scope.the_room = data;
        });
        this.join = function(queueSlug) {
            $http.post('/api/queues/' + queueSlug + '/join/');
        };

    }])
    .controller('RoomListController', ['$http', function($http){
        var value = this;
        $http.get('/api/rooms/').success(function(data){
            value.data = data;
        });
    }])
    .controller('ResourceController', ['$http', '$scope', function($http, $scope){

        $scope.queue_element = $scope.resource.current_queue_element;

    }])
    .controller('QueueElementController', ['$http', '$scope', function($http, $scope){

        $scope.delete = function() {
            $http.delete('/api/').success( function(){
                console.log('success');
            });
        };

    }]);
app.directive("customPopover", ["$popover", "$compile", function($popover, $compile) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var myPopover = $popover(element, {
                    title: 'My Title',
                    contentTemplate: '/static/hello.tpl.html',
                    html: true,
                    trigger: 'manual',
                    autoClose: true,
                    scope: scope
                });
                scope.showPopover = function() {
                    myPopover.show();
                }
            }
        }
    }]);

app.directive('queueElement', ['$http', '$scope', function($http, $scope) {

    $scope.leave() = function() {

    };
}]);
