fixed sign in and out button bg color

is public status was setting to null - added tenery if stament to fix this before creating document

not all reviews wqith status of publick showing on feed - this was because of editing rveiew was setting is pubklic back to null fixed by adding missed removal of get is pbulic from form rathwer than variable 

missing description on edit screen added as value update to be enclosed within the tags

fixed is public toggle to set when editing, did this by adding an if else statment in tmeplate 

unable to click oon edit button, edit page does not open, added url for to feed template

manually typing in your reviews into search bar breaks app, same is true for edit, delete, create screen protection added ot all - check to make sure there is a user is session var

if review id is know any user is able to delete rveiew - fixed by adding a session user, created by check