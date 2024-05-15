from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment,Bid

def listing(request,id):
    listingData = Listing.objects.get(pk=id)
    allComments = Comment.objects.filter(listing = listingData) 
    isListinginWatchlist = request.user in listingData.watchlist.all()
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListinginWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })
    
def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def index(request):
    allCategories = Category.objects.all()
    activeListings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        "listings": activeListings,
         "categories": allCategories
    })

def displayCategory(request):
    if request.method == "POST":
        allCategories = Category.objects.all()
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName = categoryFromForm)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        return render(request, "auctions/index.html", {
        "listings": activeListings,
         "categories": allCategories
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        #get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        #who is the user
        currentUser = request.user
        #get all content about a category
        categoryData = Category.objects.get(categoryName=category)
        #create a bid object
        bid = Bid(bid=float(price), user=currentUser)
        bid.save()
        #create a new object
        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=categoryData,
            owner=currentUser,
        )
        #insert the object in database
        newListing.save() 
        #redirect to index page
        return HttpResponseRedirect(reverse("index"))
    
def addBid(request,id):
    newBid = request.POST['addBid']
    listingData = Listing.objects.get(pk=id)
    allComments = Comment.objects.filter(listing = listingData) 
    isListinginWatchlist = request.user in listingData.watchlist.all()
    isOwner = request.user.username == listingData.owner.username
    if float(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=float(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid was updated successfully",
            "update": True,
            "isListingInWatchlist": isListinginWatchlist,
            "allComments": allComments,
            "isOwner": isOwner
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid updating failed",
            "update": False,
            "isListingInWatchlist": isListinginWatchlist,
            "allComments": allComments,
            "isOwner": isOwner
        })
        
def closeAuction(request,id):
    listingData = Listing.objects.get(pk=id)
    allComments = Comment.objects.filter(listing = listingData) 
    isListinginWatchlist = request.user in listingData.watchlist.all()
    isOwner = request.user.username == listingData.owner.username
    listingData.isActive = False
    listingData.save() 
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListinginWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Congratulations! Your auction is clossed."
    })


def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id) 
    message = request.POST["addComment"]
    
    newComment = Comment(
        aurthor = currentUser,
        listing = listingData,
        message = message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))
    
    