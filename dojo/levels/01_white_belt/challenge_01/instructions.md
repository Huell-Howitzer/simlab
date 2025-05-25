## White Belt Challenge 01

### Objective

In this challenge, you will:

- Create a git repository
- Make your **first commit** in Git

### Insrtuctions

#### Step 1

Create a project directory named 'project' and then enter it:

```shell
mkdir project
cd project
```

#### Step 2

Create the git repository

```shell
git init
```

You should see something like this:

```txt
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

we have a project directory but it is empty... or is it?

#### Step 3

Now we will see exactly what the `git init` command did:

- Check what is in our directory:

```shell
ls
```

> :exclamation: By default `ls` leaves out **dotfiles**

Rerun the command with the `-a`, or `--all` flag:

```shell
ls -a
```

you should see:

```txt
.  ..  .git
```

git init created a folder in our directory named `.git`

> :bulb: The .git folder is the actual **git repo**

> :memo: We can see what is in the .git folder with the `tree` command (if you have it installed):
>
>> ```txt
>> .git/
>> ├── branches
>> ├── config
>> ├── description
>> ├── HEAD
>> ├── hooks
>> │   ├── applypatch-msg.sample
>> │   ├── commit-msg.sample
>> │   ├── fsmonitor-watchman.sample
>> │   ├── post-update.sample
>> │   ├── pre-applypatch.sample
>> │   ├── pre-commit.sample
>> │   ├── pre-merge-commit.sample
>> │   ├── prepare-commit-msg.sample
>> │   ├── pre-push.sample
>> │   ├── pre-rebase.sample
>> │   ├── pre-receive.sample
>> │   ├── push-to-checkout.sample
>> │   ├── sendemail-validate.sample
>> │   └── update.sample
>> ├── info
>> │   └── exclude
>> ├── objects
>> │   ├── info
>> │   └── pack
>> └── refs
>>     ├── heads
>>     └── tags
>> ```
>
> What all this is is beyond the scope of this challenge


#### Step 4

Now let's put a folder into this directory named `README.md` (although it could be any file really)

```shell
touch README.md
```

#### Step 5

Open the file in your text editor, and add a line at the top: `# Fear Does Not Exist in This Dojo`

```shell
# You could also add the line like this but do it however you want!
echo "# Fear Does Not Exist in This Dojo" > README.md
```

Now let's **check the status of the repository**:

```shell
git status
```

**Expected Output**:

```txt
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

> :bulb: Even though we have created a file, we have not told git what we want to do with it

Git is telling us that right now, the file is **untracked** which means it is not in our version control.

> :exclamation: If we deleted the file right now it would be gone. git would not be able to restore it for us

#### Step 6

Let's add the file, and create our first commit:

```shell
git add README.md
```

- When we commit, we add a message
    - By default, git will open our text editor, and we enter our message and then save and close.
    - git uses nano (I believe) by default. If you don't like nano, or don't know what that is: [go here](#set-your-editor-configuration)
    - We can also use the `-m` flag to indicate that we are going to provide the message on the command line


```shell
git commit -m ":tada: Begin the project"
```

This message only provides a **subject line**




## Set Your Editor Configuration

```shell
# Replace gedit with whatever text editor you prefer
git config core.editor gedit
```
