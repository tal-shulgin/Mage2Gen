FROM python:3.10-slim

# Prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mage2gen

# 1. Install System Dependencies
RUN apt-get update && apt-get install -y \
    php-cli \
    php-xml \
    php-zip \
    php-curl \
    php-mbstring \
    git \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# 3. Allow Composer Plugins
RUN composer global config allow-plugins.dealerdirect/phpcodesniffer-composer-installer true

# 4. Install Magento Coding Standard
RUN composer create-project --no-dev magento/magento-coding-standard /opt/magento-coding-standard

# 5. Fix PHPCS Paths
RUN /opt/magento-coding-standard/vendor/bin/phpcs --config-set installed_paths \
/opt/magento-coding-standard,\
/opt/magento-coding-standard/vendor/phpcompatibility/php-compatibility

# Add PHPCS to PATH
ENV PATH="/opt/magento-coding-standard/vendor/bin:${PATH}"

# Copy source code
COPY . /opt/mage2gen

# Install dependencies (Added: gitingest)
RUN pip install --no-cache-dir typer jinja2 gitingest watchdog PyYAML

# Fix Permissions
RUN chmod -R 777 /opt/mage2gen

ENV PYTHONPATH="/opt/mage2gen"
ENTRYPOINT ["python3", "-m", "mage2gen.app"]