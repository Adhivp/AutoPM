import React from 'react';
import { motion } from 'framer-motion';

const techStack = [
  {
    category: 'Backend',
    technologies: ['Python', 'FastAPI', 'PostgreSQL', 'Neo4j', 'ElasticSearch']
  },
  {
    category: 'ML/AI',
    technologies: ['PyTorch', 'HuggingFace', 'scikit-learn', 'PyTorch Geometric', 'LangChain']
  },
  {
    category: 'Generative AI',
    technologies: ['Llama 3.1', 'OpenAI GPT', 'LangChain']
  },
  {
    category: 'Integrations',
    technologies: ['Jira API', 'GitHub API', 'MS Graph API', 'Confluence API']
  },
  {
    category: 'Frontend',
    technologies: ['React', 'TailwindCSS', 'Plotly', 'D3.js']
  },
  {
    category: 'Deployment',
    technologies: ['Docker', 'Kubernetes', 'Azure']
  }
];

const TechStack = () => {
  return (
    <section id="tech" className="tech-stack">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="section-header"
        >
          <h2 className="section-title">
            Powerful <span className="gradient-text">Tech Stack</span>
          </h2>
          <p className="section-subtitle">
            Built with cutting-edge technologies for maximum performance and scalability
          </p>
        </motion.div>

        <div className="tech-grid">
          {techStack.map((stack, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="tech-category"
            >
              <h3 className="tech-category-title">{stack.category}</h3>
              <div className="tech-tags">
                {stack.technologies.map((tech, techIndex) => (
                  <motion.span
                    key={techIndex}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 + techIndex * 0.05 }}
                    whileHover={{ scale: 1.1 }}
                    className="tech-tag"
                  >
                    {tech}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TechStack;
