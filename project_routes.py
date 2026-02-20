from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime

project_bp = Blueprint('project', __name__)



# Student routes for project proposal
@project_bp.route('/student/propose_project', methods=['GET', 'POST'])
@role_required('student')
def propose_project():
    """Student route to propose a new project"""
    
    # Check if student already has an active proposal
    existing_proposals = ProjectProposal.query.filter_by(
        student_id=current_user.id, 
        status='Pending'
    ).all()
    
    # Check if student is already in a group with an approved project
    student_group = GroupMember.query.filter_by(user_id=current_user.id).first()
    in_active_group = False
    if student_group:
        in_active_group = True
    
    # Get supervisors for the dropdown
    from app import User
    supervisors = User.query.filter_by(role='supervisor').all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        major = request.form.get('major')
        supervisor_id = request.form.get('supervisor_id')
        
        # Validate inputs
        if not title or not description or not major:
            flash('All fields are required', 'danger')
            return render_template('propose_project.html', 
                                  supervisors=supervisors, 
                                  existing_proposals=existing_proposals,
                                  in_active_group=in_active_group)
        
        # Create new proposal
        proposal = ProjectProposal(
            title=title,
            description=description,
            major=major,
            student_id=current_user.id,
            supervisor_id=supervisor_id if supervisor_id else None,
            status='Pending'
        )
        
        db.session.add(proposal)
        
        # Notify the supervisor if selected
        if supervisor_id:
            from app import Notification
            supervisor_notification = Notification(
                user_id=supervisor_id,
                message=f"New project proposal from {current_user.first_name} {current_user.last_name}: '{title}'",
                notification_type="project_proposal"
            )
            db.session.add(supervisor_notification)
        
        db.session.commit()
        flash('Project proposal submitted successfully! You will be notified when reviewed.', 'success')
        return redirect(url_for('project.my_proposals'))
    
    return render_template('propose_project.html', 
                          supervisors=supervisors, 
                          existing_proposals=existing_proposals,
                          in_active_group=in_active_group)

@project_bp.route('/student/my_proposals')
@role_required('student')
def my_proposals():
    """View all proposals submitted by the student"""
    proposals = ProjectProposal.query.filter_by(student_id=current_user.id).order_by(
        ProjectProposal.created_at.desc()).all()
    return render_template('my_proposals.html', proposals=proposals)

# Supervisor routes for project proposals
@project_bp.route('/supervisor/proposals')
@role_required('supervisor')
def supervisor_proposals():
    """View all proposals assigned to the supervisor"""
    proposals = ProjectProposal.query.filter_by(supervisor_id=current_user.id).order_by(
        ProjectProposal.created_at.desc()).all()
    return render_template('supervisor_proposals.html', proposals=proposals)

@project_bp.route('/supervisor/review_proposal/<int:proposal_id>', methods=['GET', 'POST'])
@role_required('supervisor')
def review_proposal(proposal_id):
    """Review and respond to a project proposal"""
    proposal = ProjectProposal.query.get_or_404(proposal_id)
    
    # Verify this proposal is assigned to the current supervisor
    if proposal.supervisor_id != current_user.id:
        flash('You do not have permission to review this proposal', 'danger')
        return redirect(url_for('project.supervisor_proposals'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        feedback = request.form.get('feedback')
        
        if action == 'approve':
            proposal.status = 'Approved'
            proposal.feedback = feedback
            
            # Now the proposal needs admin review
            # Find an admin to assign the proposal to
            from app import User
            admin = User.query.filter_by(role='admin').first()
            if admin:
                proposal.admin_id = admin.id
                
                # Notify the admin
                from app import Notification
                admin_notification = Notification(
                    user_id=admin.id,
                    message=f"Project proposal '{proposal.title}' has been approved by supervisor and needs your review",
                    notification_type="project_proposal_approved"
                )
                db.session.add(admin_notification)
            
            # Notify the student
            from app import Notification
            student_notification = Notification(
                user_id=proposal.student_id,
                message=f"Your project proposal '{proposal.title}' has been approved by supervisor and is now awaiting admin review",
                notification_type="project_proposal_update"
            )
            db.session.add(student_notification)
            
            db.session.commit()
            flash('Proposal approved and sent to admin for final review', 'success')
        
        elif action == 'reject':
            proposal.status = 'Rejected'
            proposal.feedback = feedback
            
            # Notify the student
            from app import Notification
            student_notification = Notification(
                user_id=proposal.student_id,
                message=f"Your project proposal '{proposal.title}' has been rejected by supervisor. Feedback: {feedback}",
                notification_type="project_proposal_update"
            )
            db.session.add(student_notification)
            
            db.session.commit()
            flash('Proposal rejected with feedback', 'success')
        
        return redirect(url_for('project.supervisor_proposals'))
    
    return render_template('review_proposal.html', proposal=proposal)

# Admin routes for project proposals
@project_bp.route('/admin/pending_proposals')
@role_required('admin')
def admin_pending_proposals():
    """View all proposals that have been approved by supervisors and await admin review"""
    proposals = ProjectProposal.query.filter_by(
        status='Approved',
        admin_id=current_user.id
    ).order_by(ProjectProposal.created_at.desc()).all()
    
    return render_template('admin_pending_proposals.html', proposals=proposals)

@project_bp.route('/admin/assign_evaluator/<int:proposal_id>', methods=['GET', 'POST'])
@role_required('admin')
def assign_evaluator(proposal_id):
    """Assign evaluators to a project that has been approved by a supervisor"""
    proposal = ProjectProposal.query.get_or_404(proposal_id)
    
    if proposal.status != 'Approved' or proposal.admin_id != current_user.id:
        flash('You cannot assign evaluators to this proposal', 'danger')
        return redirect(url_for('project.admin_pending_proposals'))
    
    # Get all faculty for the evaluator dropdown
    from app import User
    faculty = User.query.filter_by(role='faculty').all()
    
    if request.method == 'POST':
        evaluator_ids = request.form.getlist('evaluator_ids')
        
        if not evaluator_ids:
            flash('Please select at least one evaluator', 'danger')
            return render_template('assign_evaluator.html', proposal=proposal, faculty=faculty)
        
        # Create a new student group for this project
        last_group = StudentGroup.query.order_by(StudentGroup.id.desc()).first()
        if last_group and last_group.group_id.startswith('G'):
            try:
                last_num = int(last_group.group_id[1:])
                new_group_id = f"G{last_num + 1}"
            except ValueError:
                new_group_id = f"G{last_group.id + 1}"
        else:
            new_group_id = "G1"
        
        # Create the new group
        group = StudentGroup(
            group_id=new_group_id,
            project_title=proposal.title,
            supervisor_id=proposal.supervisor_id
        )
        db.session.add(group)
        db.session.flush()  # Get the ID without committing
        
        # Add project details
        details = ProjectDetails(
            group_id=group.id,
            description=proposal.description,
            major=proposal.major,
            progress=0
        )
        db.session.add(details)
        
        # Add the student to the group
        group_member = GroupMember(
            user_id=proposal.student_id,
            group_id=group.id
        )
        db.session.add(group_member)
        
        # Assign evaluators (teachers) to the project
        for evaluator_id in evaluator_ids:
            # Create an initial status entry for each evaluator
            status = ProjectStatus(
                status='Pending',  # Initial status
                group_id=group.id,
                teacher_id=evaluator_id,
                feedback='',
                student_feedback=''
            )
            db.session.add(status)
            
            # Notify the evaluator
            from app import Notification
            evaluator_notification = Notification(
                user_id=evaluator_id,
                message=f"You have been assigned as an evaluator for project '{proposal.title}' (Group {new_group_id})",
                notification_type="evaluator_assignment"
            )
            db.session.add(evaluator_notification)
        
        # Mark the proposal as finalized
        proposal.status = 'Finalized'
        
        # Notify the student
        from app import Notification
        student_notification = Notification(
            user_id=proposal.student_id,
            message=f"Your project proposal '{proposal.title}' has been approved and assigned to group {new_group_id}",
            notification_type="project_proposal_finalized"
        )
        db.session.add(student_notification)
        
        # Notify the supervisor
        supervisor_notification = Notification(
            user_id=proposal.supervisor_id,
            message=f"Project '{proposal.title}' has been approved and assigned to group {new_group_id}",
            notification_type="project_approved"
        )
        db.session.add(supervisor_notification)
        
        db.session.commit()
        flash(f'Project has been approved and assigned to group {new_group_id} with evaluators', 'success')
        return redirect(url_for('project.admin_pending_proposals'))
    
    return render_template('assign_evaluator.html', proposal=proposal, faculty=faculty)

# Faculty (evaluator) routes for project status updates
@project_bp.route('/faculty/assigned_projects')
@role_required('faculty')
def faculty_assigned_projects():
    """View all projects assigned to this faculty for evaluation"""
    status_entries = ProjectStatus.query.filter_by(teacher_id=current_user.id).all()
    
    # Get the unique groups
    group_ids = set(entry.group_id for entry in status_entries)
    groups = StudentGroup.query.filter(StudentGroup.id.in_(group_ids)).all()
    
    return render_template('faculty_assigned_projects.html', groups=groups, status_entries=status_entries)

@project_bp.route('/faculty/update_project_status/<int:group_id>', methods=['GET', 'POST'])
@role_required('faculty')
def update_project_status(group_id):
    """Update the status of a project as an evaluator"""
    group = StudentGroup.query.get_or_404(group_id)
    
    # Check if this faculty is assigned to evaluate this group
    status_entry = ProjectStatus.query.filter_by(
        group_id=group.id,
        teacher_id=current_user.id
    ).first()
    
    if not status_entry:
        flash('You are not assigned to evaluate this project', 'danger')
        return redirect(url_for('project.faculty_assigned_projects'))
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        feedback = request.form.get('feedback')
        student_feedback = request.form.get('student_feedback')
        
        if not new_status or not feedback or not student_feedback:
            flash('All fields are required', 'danger')
            return render_template('update_project_status.html', group=group, status_entry=status_entry)
        
        # Update the status
        status_entry.status = new_status
        status_entry.feedback = feedback
        status_entry.student_feedback = student_feedback
        status_entry.updated_at = datetime.utcnow()
        
        # Notify the student members
        from app import User, Notification
        group_members = GroupMember.query.filter_by(group_id=group.id).all()
        for member in group_members:
            notification = Notification(
                user_id=member.user_id,
                message=f"Your project '{group.project_title}' status has been updated to '{new_status}'",
                notification_type="project_status_update"
            )
            db.session.add(notification)
        
        # Notify the supervisor
        if group.supervisor_id:
            notification = Notification(
                user_id=group.supervisor_id,
                message=f"Project '{group.project_title}' (Group {group.group_id}) status has been updated to '{new_status}'",
                notification_type="project_status_update"
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('Project status updated successfully', 'success')
        return redirect(url_for('project.faculty_assigned_projects'))
    
    return render_template('update_project_status.html', group=group, status_entry=status_entry)

# Routes for tracking project milestones
@project_bp.route('/add_milestone/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_milestone(group_id):
    """Add a milestone for a project"""
    group = StudentGroup.query.get_or_404(group_id)
    
    # Check permissions - only supervisor or admin can add milestones
    if current_user.role not in ['supervisor', 'admin'] or \
       (current_user.role == 'supervisor' and current_user.id != group.supervisor_id):
        flash('You do not have permission to add milestones for this project', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        if not title or not due_date_str:
            flash('Title and due date are required', 'danger')
            return render_template('add_milestone.html', group=group)
        
        # Parse the date
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return render_template('add_milestone.html', group=group)
        
        milestone = ProjectMilestone(
            title=title,
            description=description,
            due_date=due_date,
            group_id=group.id
        )
        
        db.session.add(milestone)
        
        # Notify group members
        from app import Notification
        group_members = GroupMember.query.filter_by(group_id=group.id).all()
        for member in group_members:
            notification = Notification(
                user_id=member.user_id,
                message=f"New milestone added to your project: '{title}' due on {due_date_str}",
                notification_type="new_milestone"
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('Milestone added successfully', 'success')
        
        # Redirect based on role
        if current_user.role == 'supervisor':
            return redirect(url_for('dashboard_supervisor'))
        else:
            return redirect(url_for('dashboard_admin'))
    
    return render_template('add_milestone.html', group=group)

@project_bp.route('/update_milestone_status/<int:milestone_id>', methods=['POST'])
@login_required
def update_milestone_status(milestone_id):
    """Update the status of a milestone"""
    milestone = ProjectMilestone.query.get_or_404(milestone_id)
    
    # Check if current user is a member of the group, the supervisor, or an admin
    is_group_member = GroupMember.query.filter_by(
        user_id=current_user.id, 
        group_id=milestone.group_id
    ).first() is not None
    
    is_supervisor = current_user.role == 'supervisor' and \
                   milestone.group.supervisor_id == current_user.id
    
    if not (is_group_member or is_supervisor or current_user.role == 'admin'):
        flash('You do not have permission to update this milestone', 'danger')
        return redirect(url_for('index'))
    
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'Completed', 'Late']:
        flash('Invalid status', 'danger')
    else:
        milestone.status = new_status
        db.session.commit()
        flash('Milestone status updated', 'success')
    
    # Redirect based on role
    if current_user.role == 'student':
        return redirect(url_for('dashboard_student'))
    elif current_user.role == 'supervisor':
        return redirect(url_for('dashboard_supervisor'))
    else:
        return redirect(url_for('dashboard_admin'))

# Route to update project progress
@project_bp.route('/update_project_progress/<int:group_id>', methods=['POST'])
@login_required
def update_project_progress(group_id):
    """Update the progress percentage of a project"""
    group = StudentGroup.query.get_or_404(group_id)
    
    # Check permissions - supervisor, admin, or group member can update progress
    is_group_member = GroupMember.query.filter_by(
        user_id=current_user.id, 
        group_id=group.id
    ).first() is not None
    
    is_supervisor = current_user.role == 'supervisor' and \
                   group.supervisor_id == current_user.id
    
    if not (is_group_member or is_supervisor or current_user.role == 'admin'):
        flash('You do not have permission to update this project', 'danger')
        return redirect(url_for('index'))
    
    progress = request.form.get('progress')
    try:
        progress = int(progress)
        if 0 <= progress <= 100:
            # Get or create project details
            details = ProjectDetails.query.filter_by(group_id=group.id).first()
            if not details:
                details = ProjectDetails(group_id=group.id)
                db.session.add(details)
            
            details.progress = progress
            details.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Project progress updated', 'success')
        else:
            flash('Progress must be between 0 and 100', 'danger')
    except ValueError:
        flash('Invalid progress value', 'danger')
    
    # Redirect based on role
    if current_user.role == 'student':
        return redirect(url_for('dashboard_student'))
    elif current_user.role == 'supervisor':
        return redirect(url_for('dashboard_supervisor'))
    else:
        return redirect(url_for('dashboard_admin')) 