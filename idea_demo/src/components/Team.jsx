import React from 'react';
import { motion } from 'framer-motion';
import { Github, Linkedin, Mail, Award } from 'lucide-react';

const Team = () => {
  const teamMembers = [
    {
      name: 'Adhithyan VP',
      role: 'Full Stack Developer & ML Engineer',
      avatar: '👨‍💻',
      description: 'Specializes in AI/ML integration and backend architecture',
      socials: {
        github: 'https://github.com/Adhivp',
        linkedin: 'https://www.linkedin.com/in/adhithyan-vp-5b8b87246/',
        email: 'adhivp910@gmail.com'
      }
    },
    {
      name: 'Sreya Suresh',
      role: 'Frontend Developer & UX Designer',
      avatar: '👩‍💻',
      description: 'Focuses on user experience and responsive design',
      socials: {
        github: null,
        linkedin: null, // Add Sreya's LinkedIn if available
        email: 'sreyadelna@gmail.com'
      }
    }
  ];

  return (
    <section id="team" className="team">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="section-header"
        >
          <h2 className="section-title">
            Meet <span className="gradient-text">Porotta Pythoners</span>
          </h2>
          <p className="section-subtitle">
            Team Category • Problem Statement AH2025/PS02
          </p>
        </motion.div>

        <div className="team-grid">
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              whileHover={{ y: -10 }}
              className="team-card"
            >
              <div className="team-avatar">{member.avatar}</div>
              <h3 className="team-name">{member.name}</h3>
              <div className="team-role">{member.role}</div>
              <p className="team-description">{member.description}</p>
              <div className="team-socials">
                {member.socials.github && (
                  <motion.a
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                    href={member.socials.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label="GitHub"
                  >
                    <Github size={20} />
                  </motion.a>
                )}
                {member.socials.linkedin && (
                  <motion.a
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                    href={member.socials.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label="LinkedIn"
                  >
                    <Linkedin size={20} />
                  </motion.a>
                )}
                {member.socials.email && (
                  <motion.a
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                    href={`mailto:${member.socials.email}`}
                    className="social-link"
                    aria-label="Email"
                  >
                    <Mail size={20} />
                  </motion.a>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="project-info"
        >
          <div className="info-card">
            <Award className="info-icon" />
            <div className="info-content">
              <h4 className="info-title">Problem Statement</h4>
              <p className="info-text">AI-Powered Project Management Assistant</p>
            </div>
          </div>
          <div className="info-card">
            <Award className="info-icon" />
            <div className="info-content">
              <h4 className="info-title">Innovation Focus</h4>
              <p className="info-text">Proactive Intelligence for Automotive Projects</p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Team;
